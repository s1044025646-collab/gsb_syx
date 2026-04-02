import { useEffect, useRef, useState } from "react";
import DualMetricChart from "../components/DualMetricChart";

const LOSS = [2.84, 2.61, 2.45, 2.31, 2.18, 2.05, 1.94, 1.88, 1.82, 1.76];
const ACC = [0.62, 0.64, 0.66, 0.68, 0.71, 0.73, 0.75, 0.77, 0.78, 0.79];

const LOG_SEED = [
  "[08:12:01] 正在下载全局参数…",
  "[08:12:04] 校验聚合签名通过",
  "[08:12:09] 正在生成本地梯度…",
  "[08:12:14] 应用本地 DP 裁剪 ε=1.2",
  "[08:12:18] 加密梯度包大小 4.2MB",
  "[08:12:22] 排队上传至安全中继…",
];

export default function MonitorPage() {
  const [logs, setLogs] = useState(LOG_SEED);
  const [progress, setProgress] = useState(46);
  const tick = useRef(0);

  useEffect(() => {
    const timer = setInterval(() => {
      tick.current += 1;
      setProgress((p) => Math.min(99, p + (Math.random() > 0.7 ? 1 : 0)));
      setLogs((prev) => {
        const line = `[${new Date().toLocaleTimeString("zh-CN")}] 迭代步进 +1 · loss 估计下降中`;
        return [...prev.slice(-40), line];
      });
    }, 2800);
    return () => clearInterval(timer);
  }, []);

  const logRef = useRef(null);
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="page monitor-page">
      <header className="page-head">
        <h1>训练监控</h1>
        <p className="muted">
          实时曲线与指标为离线预览；联机环境需对接协调器与节点代理。
        </p>
      </header>

      <section className="panel">
        <h2>总进度</h2>
        <div className="big-progress">
          <div className="progress-track tall">
            <div
              className="progress-fill gradient"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="big-pct">{progress}%</span>
        </div>
      </section>

      <section className="panel">
        <h2>实时双曲线</h2>
        <p className="muted small">
          <span className="legend-inline loss">红线 Global Loss（下降中）</span>
          {" · "}
          <span className="legend-inline acc">蓝线 Local Accuracy（本院贡献）</span>
        </p>
        <DualMetricChart
          lossSeries={LOSS.map((v) => v + Math.random() * 0.06)}
          accSeries={ACC.map((v) => v + Math.random() * 0.015)}
          width={560}
          height={220}
        />
      </section>

      <section className="metrics-row">
        <div className="metric-card">
          <span className="metric-label">证明生成耗时</span>
          <strong>180ms</strong>
          <span className="metric-pill ok">ZK-Proof status: Validated</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">网络带宽</span>
          <strong>RDMA 100Gbps</strong>
          <span className="metric-pill ok">已连接</span>
        </div>
      </section>

      <section className="panel log-panel">
        <h2>节点日志</h2>
        <div className="log-window" ref={logRef} tabIndex={0}>
          {logs.map((line, i) => (
            <div key={`${i}-${line.slice(0, 20)}`} className="log-line">
              {line}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
