import { useCallback, useRef, useState } from 'react';
import {
  ReactFlow,
  addEdge,
  useNodesState,
  useEdgesState,
  Background,
  Controls,
  MiniMap,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import ComponentNode from './nodes/ComponentNode';
import FormulaNode from './nodes/FormulaNode';
import OutputNode from './nodes/OutputNode';

const nodeTypes = { component: ComponentNode, formula: FormulaNode, output: OutputNode };

const FORMULA_OPTIONS = [
  { value: 'voltage_divider', label: '分圧回路' },
  { value: 'add', label: '加算' },
  { value: 'multiply', label: '乗算' },
  { value: 'divide', label: '除算' },
];

const defaultNodes = [
  {
    id: 'r1', type: 'component', position: { x: 60, y: 80 },
    data: { label: 'R1', symbol: 'R1', params: { typ_value: 1000, room_temp_tolerance: 1, temp_coefficient: 50 } },
  },
  {
    id: 'r2', type: 'component', position: { x: 60, y: 260 },
    data: { label: 'R2', symbol: 'R2', params: { typ_value: 1000, room_temp_tolerance: 1, temp_coefficient: 50 } },
  },
  {
    id: 'vin', type: 'component', position: { x: 60, y: 440 },
    data: { label: 'Vin', symbol: 'Vin', params: { typ_value: 5.0, room_temp_tolerance: 0.1, temp_coefficient: 10 } },
  },
  {
    id: 'formula1', type: 'formula', position: { x: 360, y: 240 },
    data: { label: '分圧回路', formulaType: 'voltage_divider', connectedSymbols: ['R1', 'R2', 'Vin'] },
  },
  {
    id: 'output1', type: 'output', position: { x: 660, y: 200 },
    data: { label: '出力', result: null, loading: false, error: null, sensitivity: null },
  },
];

const defaultEdges = [
  { id: 'e-r1-f', source: 'r1', target: 'formula1' },
  { id: 'e-r2-f', source: 'r2', target: 'formula1' },
  { id: 'e-vin-f', source: 'vin', target: 'formula1' },
  { id: 'e-f-o', source: 'formula1', target: 'output1' },
];

let nodeIdCounter = 10;

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(defaultNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(defaultEdges);
  const [temperature, setTemperature] = useState(25);
  const [numSims, setNumSims] = useState(10000);
  const [selectedFormula, setSelectedFormula] = useState('voltage_divider');
  const [newSymbol, setNewSymbol] = useState('');
  const nodeParamsRef = useRef({});

  const onConnect = useCallback((params) => setEdges(eds => addEdge(params, eds)), [setEdges]);

  const getComponentParams = useCallback(() => {
    return nodes
      .filter(n => n.type === 'component')
      .map(n => ({
        symbol: n.data.symbol,
        ...(nodeParamsRef.current[n.id] || n.data.params),
      }));
  }, [nodes]);

  const getConnectedSymbols = useCallback((formulaId) => {
    const sourceIds = edges
      .filter(e => e.target === formulaId)
      .map(e => e.source);
    return nodes
      .filter(n => sourceIds.includes(n.id) && n.type === 'component')
      .map(n => n.data.symbol);
  }, [nodes, edges]);

  const getFormulaForOutput = useCallback((outputId) => {
    const formulaEdge = edges.find(e => e.target === outputId);
    if (!formulaEdge) return null;
    return nodes.find(n => n.id === formulaEdge.source && n.type === 'formula') || null;
  }, [nodes, edges]);

  const runSimulation = useCallback(async () => {
    const outputNodes = nodes.filter(n => n.type === 'output');
    if (outputNodes.length === 0) return;

    setNodes(nds => nds.map(n =>
      n.type === 'output' ? { ...n, data: { ...n.data, loading: true, error: null, result: null, sensitivity: null } } : n
    ));

    const componentParams = getComponentParams();

    for (const outputNode of outputNodes) {
      const formulaNode = getFormulaForOutput(outputNode.id);
      if (!formulaNode) {
        setNodes(nds => nds.map(n =>
          n.id === outputNode.id ? { ...n, data: { ...n.data, loading: false, error: '演算ノードが接続されていません' } } : n
        ));
        continue;
      }

      const symbols = getConnectedSymbols(formulaNode.id);
      if (symbols.length === 0) {
        setNodes(nds => nds.map(n =>
          n.id === outputNode.id ? { ...n, data: { ...n.data, loading: false, error: 'コンポーネントが接続されていません' } } : n
        ));
        continue;
      }

      try {
        const [simRes, sensRes] = await Promise.all([
          fetch('http://localhost:8000/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              components: componentParams,
              formula_type: formulaNode.data.formulaType,
              component_symbols: symbols,
              temperature,
              num_simulations: numSims,
            }),
          }).then(r => r.json()),
          fetch('http://localhost:8000/sensitivity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              components: componentParams,
              formula_type: formulaNode.data.formulaType,
              component_symbols: symbols,
              temperature,
              delta: 1.0,
            }),
          }).then(r => r.json()),
        ]);

        setNodes(nds => nds.map(n =>
          n.id === outputNode.id
            ? { ...n, data: { ...n.data, loading: false, result: simRes, sensitivity: sensRes } }
            : n
        ));
      } catch (err) {
        setNodes(nds => nds.map(n =>
          n.id === outputNode.id ? { ...n, data: { ...n.data, loading: false, error: 'APIエラー: ' + err.message } } : n
        ));
      }
    }
  }, [nodes, edges, temperature, numSims, getComponentParams, getConnectedSymbols, getFormulaForOutput, setNodes]);

  const addComponentNode = () => {
    const symbol = newSymbol.trim() || `C${nodeIdCounter}`;
    const id = `node-${nodeIdCounter++}`;
    setNodes(nds => [...nds, {
      id, type: 'component', position: { x: 60, y: 80 + (nds.length % 6) * 180 },
      data: {
        label: symbol, symbol,
        params: { typ_value: 1000, room_temp_tolerance: 1, temp_coefficient: 50 },
        onChange: (p) => { nodeParamsRef.current[id] = p; },
      },
    }]);
    setNewSymbol('');
  };

  const addFormulaNode = () => {
    const id = `formula-${nodeIdCounter++}`;
    setNodes(nds => [...nds, {
      id, type: 'formula', position: { x: 360, y: 240 },
      data: { label: selectedFormula, formulaType: selectedFormula, connectedSymbols: [] },
    }]);
  };

  const addOutputNode = () => {
    const id = `output-${nodeIdCounter++}`;
    setNodes(nds => [...nds, {
      id, type: 'output', position: { x: 660, y: 200 },
      data: { label: '出力', result: null, loading: false, error: null, sensitivity: null },
    }]);
  };

  return (
    <div style={{ width: '100vw', height: '100vh', background: '#0a0f1a', display: 'flex', flexDirection: 'column' }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 12, padding: '8px 16px',
        background: '#0d1b2a', borderBottom: '1px solid #1e3a5f',
        flexWrap: 'wrap',
      }}>
        <span style={{ color: '#4fc3f7', fontWeight: 'bold', fontFamily: 'monospace', fontSize: 14 }}>
          誤差伝播ビジュアライザ
        </span>

        <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          <input
            value={newSymbol}
            onChange={e => setNewSymbol(e.target.value)}
            placeholder="シンボル名 (例: R3)"
            style={inputStyle}
          />
          <button onClick={addComponentNode} style={btnStyle('#2d6a9f')}>+ コンポーネント</button>
        </div>

        <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          <select
            value={selectedFormula}
            onChange={e => setSelectedFormula(e.target.value)}
            style={{ ...inputStyle, cursor: 'pointer' }}
          >
            {FORMULA_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
          <button onClick={addFormulaNode} style={btnStyle('#7b52ab')}>+ 演算</button>
        </div>

        <button onClick={addOutputNode} style={btnStyle('#388e3c')}>+ 出力</button>

        <div style={{ display: 'flex', gap: 6, alignItems: 'center', marginLeft: 'auto' }}>
          <label style={labelStyle}>温度</label>
          <input type="number" value={temperature} onChange={e => setTemperature(+e.target.value)} style={{ ...inputStyle, width: 60 }} />
          <label style={labelStyle}>℃</label>
          <label style={labelStyle}>試行回数</label>
          <input type="number" value={numSims} onChange={e => setNumSims(+e.target.value)} style={{ ...inputStyle, width: 80 }} />
          <button onClick={runSimulation} style={{ ...btnStyle('#c62828'), padding: '6px 20px', fontWeight: 'bold' }}>
            ▶ 実行
          </button>
        </div>
      </div>

      <div style={{ flex: 1 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          style={{ background: '#0a0f1a' }}
        >
          <Background color="#1e3a5f" gap={20} />
          <Controls style={{ background: '#0d1b2a', border: '1px solid #1e3a5f' }} />
          <MiniMap style={{ background: '#0d1b2a' }} nodeColor="#2d6a9f" />
        </ReactFlow>
      </div>
    </div>
  );
}

const inputStyle = {
  background: '#0d1b2a',
  border: '1px solid #2d6a9f',
  color: '#e0f0ff',
  borderRadius: 4,
  padding: '4px 8px',
  fontFamily: 'monospace',
  fontSize: 12,
};

const labelStyle = { color: '#90caf9', fontFamily: 'monospace', fontSize: 12 };

const btnStyle = (bg) => ({
  background: bg,
  color: '#fff',
  border: 'none',
  borderRadius: 4,
  padding: '4px 10px',
  cursor: 'pointer',
  fontFamily: 'monospace',
  fontSize: 12,
});
