import { useMemo, useSyncExternalStore } from "react";
import SparkLineChart from "../components/SparkLineChart";
import { getLocalFiles, totalDataBytes } from "../utils/storage";

function subscribeFiles(cb) {
  window.addEventListener("medfl-storage", cb);
  return () => window.removeEventListener("medfl-storage", cb);
}

function readFilesSnapshot() {
  return getLocalFiles();
}

const CITIES = [
  { name: "上海", hospital: "市一医院", x: 78, y: 52, online: true },
  { name: "北京", hospital: "肿瘤中心", x: 62, y: 28, online: true },
  { name: "广州", hospital: "中山附一", x: 58, y: 72, online: true },
  { name: "成都", hospital: "华西医院", x: 42, y: 55, online: false },
  { name: "杭州", hospital: "浙大附二", x: 72, y: 48, online: true },
];

const COMPUTE_7D = [12.4, 14.1, 11.8, 16.2, 15.0, 18.3, 17.6];
const CONTRIB_7D = [0.12, 0.14, 0.11, 0.16, 0.15, 0.18, 0.19];

const NOTICES = [
  {
    id: 1,
    time: "10:24",
    text: "张老师发起了新的肺癌筛查训练任务，欢迎符合条件的节点在「任务」页申请加入。",
    type: "task",
  },
  {
    id: 2,
    time: "昨天",
    text: "联邦调度中心：本周三 02:00–04:00 计划维护聚合服务，本地训练可照常进行。",
    type: "ops",
  },
  {
    id: 3,
    time: "12-20",
    text: "安全审计：本院节点已通过上一轮隐私合规抽检（仅本地策略，无原始数据出境）。",
    type: "audit",
  },
];

function formatBytes(n) {
  if (n < 1024) return `${n} B`;
  if (n < 1024 ** 2) return `${(n / 1024).toFixed(1)} KB`;
  if (n < 1024 ** 3) return `${(n / 1024 ** 2).toFixed(1)} MB`;
  return `${(n / 1024 ** 3).toFixed(2)} GB`;
}

export default function Overview() {
  const files = useSyncExternalStore(
    subscribeFiles,
    readFilesSnapshot,
    readFilesSnapshot
  );
  const dataTotal = useMemo(() => totalDataBytes(), [files]);
  const activeTasks = 3;
  const onlineNodes = CITIES.filter((c) => c.online).length;

  return (
    <div className="page overview-page">
      <header className="page-head">
        <h1>协作概览</h1>
        <p className="muted">
          实时反映本院登记数据规模、参与任务与节点连通状态（随「数据」页登记变更）。
        </p>
      </header>

      <section className="stat-row">
        <div className="stat-card">
          <span className="stat-label">数据总量</span>
          <strong className="stat-value">{formatBytes(dataTotal)}</strong>
          <span className="stat-sub">{files.length} 个本地登记文件</span>
        </div>
        <div className="stat-card accent">
          <span className="stat-label">参与任务</span>
          <strong className="stat-value">{activeTasks}</strong>
          <span className="stat-sub">进行中联邦项目</span>
        </div>
        <div className="stat-card ok">
          <span className="stat-label">节点状态</span>
          <strong className="stat-value">在线</strong>
          <span className="stat-sub">与协调器心跳正常 · TLS 1.3</span>
        </div>
      </section>

      <section className="overview-split">
        <div className="panel map-panel">
          <h2>全网协作地图</h2>
          <p className="muted small">
            示意：圆点表示协作医院节点位置与在线状态。
          </p>
          <div className="map-stage">
            <div className="map-grid" />
            {CITIES.map((c) => (
              <div
                key={c.name}
                className={`city-pin ${c.online ? "on" : "off"}`}
                style={{ left: `${c.x}%`, top: `${c.y}%` }}
                title={`${c.hospital}`}
              >
                <span className="pin-dot" />
                <span className="pin-label">{c.name}</span>
              </div>
            ))}
          </div>
          <ul className="map-legend">
            <li>
              <i className="dot on" /> 在线 {onlineNodes} 城
            </li>
            <li>
              <i className="dot off" /> 离线 {CITIES.length - onlineNodes} 城
            </li>
          </ul>
        </div>

        <div className="panel chart-panel">
          <h2>训练动态（近 7 天）</h2>
          <p className="muted small">
            左：算力消耗（TFLOPs·h 等效）；右：本院对全局目标的贡献度指数。
          </p>
          <div className="twin-charts">
            <SparkLineChart
              series={COMPUTE_7D}
              width={340}
              height={150}
              color="#0ea5e9"
              label="算力消耗趋势"
            />
            <SparkLineChart
              series={CONTRIB_7D.map((v) => v * 100)}
              width={340}
              height={150}
              color="#10b981"
              label="贡献度指数"
            />
          </div>
          <div className="day-labels">
            {["一", "二", "三", "四", "五", "六", "日"].map((d) => (
              <span key={d}>周{d}</span>
            ))}
          </div>
        </div>
      </section>

      <section className="panel notice-panel">
        <h2>系统通知</h2>
        <ul className="notice-list">
          {NOTICES.map((n) => (
            <li key={n.id} className={`notice-item ${n.type}`}>
              <time>{n.time}</time>
              <p>{n.text}</p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
