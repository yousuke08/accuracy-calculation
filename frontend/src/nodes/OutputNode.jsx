import { Handle, Position } from '@xyflow/react';

function Bar({ label, value, nominal, color }) {
  if (value == null || nominal == null || nominal === 0) return null;
  const pct = ((value - nominal) / Math.abs(nominal)) * 100;
  return (
    <div style={{ marginBottom: 3 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: '#b0bec5' }}>
        <span>{label}</span>
        <span style={{ color }}>{pct >= 0 ? '+' : ''}{pct.toFixed(2)}%</span>
      </div>
    </div>
  );
}

export default function OutputNode({ data, selected }) {
  const r = data.result;

  return (
    <div style={{
      background: selected ? '#1a2e1e' : '#162418',
      border: `2px solid ${selected ? '#66bb6a' : '#388e3c'}`,
      borderRadius: 10,
      padding: '10px 14px',
      minWidth: 220,
      color: '#e8f5e9',
      fontFamily: 'monospace',
      fontSize: 12,
    }}>
      <div style={{ fontWeight: 'bold', marginBottom: 8, color: '#66bb6a', fontSize: 13 }}>
        📊 出力 / 誤差結果
      </div>

      {data.loading && <div style={{ color: '#aaa' }}>計算中...</div>}
      {data.error && <div style={{ color: '#ef5350' }}>{data.error}</div>}

      {r && !data.loading && (
        <>
          <div style={{ marginBottom: 6 }}>
            <span style={{ color: '#a5d6a7' }}>公称値: </span>
            <span>{r.nominal_output?.toExponential(4)}</span>
          </div>
          <div style={{ marginBottom: 6 }}>
            <span style={{ color: '#a5d6a7' }}>平均値: </span>
            <span>{r.average_output?.toExponential(4)}</span>
          </div>
          <div style={{ borderTop: '1px solid #2e4d30', paddingTop: 6, marginBottom: 4 }}>
            <div style={{ color: '#a5d6a7', marginBottom: 3 }}>誤差範囲</div>
            <Bar label="最小" value={r.min_output} nominal={r.nominal_output} color="#4fc3f7" />
            <Bar label="平均" value={r.average_output} nominal={r.nominal_output} color="#fff176" />
            <Bar label="最大" value={r.max_output} nominal={r.nominal_output} color="#ef9a9a" />
          </div>
          <div style={{ borderTop: '1px solid #2e4d30', paddingTop: 6 }}>
            <div style={{ color: '#a5d6a7', marginBottom: 3 }}>標準偏差</div>
            <span>{r.std_dev_output?.toExponential(4)}</span>
          </div>
          {data.sensitivity && (
            <div style={{ borderTop: '1px solid #2e4d30', paddingTop: 6, marginTop: 6 }}>
              <div style={{ color: '#a5d6a7', marginBottom: 3 }}>感度解析</div>
              {Object.entries(data.sensitivity).map(([sym, val]) => (
                <div key={sym} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11 }}>
                  <span style={{ color: '#b0bec5' }}>{sym}</span>
                  <span style={{ color: Math.abs(val) > 0.5 ? '#ef9a9a' : '#fff176' }}>{val?.toFixed(4)}</span>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {!r && !data.loading && !data.error && (
        <div style={{ color: '#555', fontSize: 11 }}>接続して「実行」してください</div>
      )}

      <Handle type="target" position={Position.Left} style={{ background: '#66bb6a', width: 10, height: 10 }} />
    </div>
  );
}
