import { useId } from "react";

/** 轻量 SVG 折线图，无第三方依赖 */
export default function SparkLineChart({
  series,
  width = 360,
  height = 140,
  color = "#0ea5e9",
  label,
  fillOpacity = 0.12,
}) {
  const gradId = useId().replace(/:/g, "");
  if (!series?.length) return null;
  const pad = 8;
  const w = width - pad * 2;
  const h = height - pad * 2;
  const min = Math.min(...series);
  const max = Math.max(...series);
  const span = max - min || 1;
  const pts = series.map((v, i) => {
    const x = pad + (i / (series.length - 1 || 1)) * w;
    const y = pad + h - ((v - min) / span) * h;
    return `${x},${y}`;
  });
  const d = `M ${pts.join(" L ")}`;
  const area = `${d} L ${pad + w} ${pad + h} L ${pad} ${pad + h} Z`;

  return (
    <div className="chart-wrap">
      {label && <span className="chart-label">{label}</span>}
      <svg width={width} height={height} className="spark-svg" aria-hidden>
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={fillOpacity * 2} />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={area} fill={`url(#${gradId})`} stroke="none" />
        <path
          d={d}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
}
