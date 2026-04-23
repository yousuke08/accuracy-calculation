import { Handle, Position } from '@xyflow/react';

const FORMULAS = {
  voltage_divider: '分圧回路  Vout = Vin × R2/(R1+R2)',
  add: '加算  A + B + ...',
  multiply: '乗算  A × B × ...',
  divide: '除算  A ÷ B',
};

export default function FormulaNode({ data, selected }) {
  return (
    <div style={{
      background: selected ? '#2a1e3f' : '#1e1a2e',
      border: `2px solid ${selected ? '#ce93d8' : '#7b52ab'}`,
      borderRadius: 10,
      padding: '10px 14px',
      minWidth: 240,
      color: '#f3e5ff',
      fontFamily: 'monospace',
      fontSize: 12,
    }}>
      <div style={{ fontWeight: 'bold', marginBottom: 8, color: '#ce93d8', fontSize: 13 }}>
        ∑ 演算ノード
      </div>
      <div style={{ color: '#ba68c8', fontSize: 11 }}>
        {FORMULAS[data.formulaType] || data.formulaType}
      </div>
      <div style={{ marginTop: 6, color: '#d1c4e9', fontSize: 11 }}>
        入力: {data.connectedSymbols?.join(', ') || '未接続'}
      </div>
      <Handle type="target" position={Position.Left} style={{ background: '#ce93d8', width: 10, height: 10 }} />
      <Handle type="source" position={Position.Right} style={{ background: '#ce93d8', width: 10, height: 10 }} />
    </div>
  );
}
