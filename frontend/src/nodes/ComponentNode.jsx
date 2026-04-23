import { Handle, Position } from '@xyflow/react';
import { useState } from 'react';

export default function ComponentNode({ data, selected }) {
  const [params, setParams] = useState(data.params || {
    typ_value: 1000,
    room_temp_tolerance: 1,
    temp_coefficient: 50,
  });

  const update = (key, value) => {
    const updated = { ...params, [key]: parseFloat(value) || 0 };
    setParams(updated);
    data.onChange?.(updated);
  };

  return (
    <div style={{
      background: selected ? '#1e3a5f' : '#1a2a3a',
      border: `2px solid ${selected ? '#4fc3f7' : '#2d6a9f'}`,
      borderRadius: 10,
      padding: '10px 14px',
      minWidth: 200,
      color: '#e0f0ff',
      fontFamily: 'monospace',
      fontSize: 12,
    }}>
      <div style={{ fontWeight: 'bold', marginBottom: 8, color: '#4fc3f7', fontSize: 13 }}>
        ⚡ {data.label}
      </div>
      {[
        { key: 'typ_value', label: '公称値' },
        { key: 'room_temp_tolerance', label: '公差 (%)' },
        { key: 'temp_coefficient', label: '温度係数 (ppm/℃)' },
      ].map(({ key, label }) => (
        <div key={key} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, gap: 6 }}>
          <span style={{ color: '#90caf9' }}>{label}</span>
          <input
            type="number"
            value={params[key]}
            onChange={e => update(key, e.target.value)}
            style={{
              width: 70,
              background: '#0d1b2a',
              border: '1px solid #2d6a9f',
              color: '#e0f0ff',
              borderRadius: 4,
              padding: '1px 4px',
              fontFamily: 'monospace',
              fontSize: 12,
            }}
          />
        </div>
      ))}
      <Handle type="source" position={Position.Right} style={{ background: '#4fc3f7', width: 10, height: 10 }} />
    </div>
  );
}
