import { NavLink, Outlet } from "react-router-dom";

const nav = [
  { to: "/", label: "概览", icon: "◈" },
  { to: "/data", label: "数据", icon: "▤" },
  { to: "/tasks", label: "任务", icon: "◎" },
  { to: "/monitor", label: "监控", icon: "◉" },
  { to: "/results", label: "成果", icon: "✦" },
];

export default function AppLayout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-icon" />
          <div>
            <strong>Med-FL</strong>
            <small>医疗联邦学习 · 节点端</small>
          </div>
        </div>
        <nav className="side-nav">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <span className="nav-ico">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <p className="side-foot">
          所有敏感配置与数据登记仅保存在本机浏览器，默认不外传。
        </p>
      </aside>
      <div className="main-area">
        <Outlet />
      </div>
    </div>
  );
}
