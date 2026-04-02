/** 双折线：左轴 loss，右轴 accuracy（归一化到同一画布高度） */
export default function DualMetricChart({
  lossSeries,
  accSeries,
  width = 520,
  height = 200,
}) {
  const pad = { t: 12, r: 12, b: 28, l: 44 };
  const w = width - pad.l - pad.r;
  const h = height - pad.t - pad.b;

  const norm = (arr, invert = false) => {
    const min = Math.min(...arr);
    const max = Math.max(...arr);
    const span = max - min || 1;
    return arr.map((v, i) => {
      let t = (v - min) / span;
      if (invert) t = 1 - t;
      const x = pad.l + (i / (arr.length - 1 || 1)) * w;
      const y = pad.t + t * h;
      return { x, y };
    });
  };

  const lossPts = norm(lossSeries, true);
  const accPts = norm(accSeries, false);

  const line = (pts) =>
    pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");

  return (
    <svg width={width} height={height} className="dual-chart" aria-label="训练指标">
      <text x={pad.l} y={14} className="axis-tag loss-tag">
        Global Loss ↓
      </text>
      <text x={width - pad.r - 120} y={14} className="axis-tag acc-tag">
        Local Accuracy
      </text>
      <line
        x1={pad.l}
        y1={pad.t + h}
        x2={pad.l + w}
        y2={pad.t + h}
        stroke="var(--border)"
        strokeWidth="1"
      />
      <path
        d={line(lossPts)}
        fill="none"
        stroke="#ef4444"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      <path
        d={line(accPts)}
        fill="none"
        stroke="#3b82f6"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeDasharray="6 4"
      />
      <text x={pad.l} y={height - 6} className="axis-caption">
        迭代步
      </text>
    </svg>
  );
}
