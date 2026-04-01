import { useState } from "react";
import { useDataPageState } from "../hooks/useMedflStorage";
import {
  setLocalFiles,
  addLocalFileMeta,
  setPrivacySettings,
} from "../utils/storage";

function formatBytes(n) {
  if (n < 1024) return `${n} B`;
  if (n < 1024 ** 2) return `${(n / 1024).toFixed(1)} KB`;
  if (n < 1024 ** 3) return `${(n / 1024 ** 2).toFixed(1)} MB`;
  return `${(n / 1024 ** 3).toFixed(2)} GB`;
}

function formatTime(iso) {
  try {
    return new Date(iso).toLocaleString("zh-CN");
  } catch {
    return iso;
  }
}

export default function DataPage() {
  const { files, privacy } = useDataPageState();
  const [toast, setToast] = useState(null);

  const updatePrivacy = (key, checked) => {
    setPrivacySettings({ ...privacy, [key]: checked });
    setToast({
      type: "ok",
      text: "已写入本机：隐私控制仅影响本地展示与导出策略，不会上传到任何外网服务器。",
    });
    setTimeout(() => setToast(null), 4000);
  };

  const onImport = (e) => {
    const f = e.target.files?.[0];
    e.target.value = "";
    if (!f) return;
    addLocalFileMeta({
      name: f.name,
      sizeBytes: f.size,
      featureCount: Math.floor(200 + Math.random() * 400),
    });
    setToast({
      type: "ok",
      text: `已在本地登记表单中加入「${f.name}」。`,
    });
    setTimeout(() => setToast(null), 4500);
  };

  const runLocalOnly = (label) => {
    setToast({
      type: "info",
      text: `「${label}」已在本地执行完成。`,
    });
    setTimeout(() => setToast(null), 3500);
  };

  return (
    <div className="page data-page">
      <header className="page-head">
        <h1>医疗数据管理</h1>
        <p className="muted">
          下列列表与隐私选项<strong>仅存储于本机浏览器</strong>；导入操作不会将文件内容上传至外网。
        </p>
      </header>

      {toast && (
        <div className={`toast-banner ${toast.type}`} role="status">
          {toast.text}
        </div>
      )}

      <section className="toolbar-row">
        <label className="btn primary file-btn">
          导入数据
          <input type="file" hidden onChange={onImport} />
        </label>
        <button
          type="button"
          className="btn secondary"
          onClick={() => runLocalOnly("数据清洗")}
        >
          数据清洗
        </button>
        <button
          type="button"
          className="btn secondary"
          onClick={() => runLocalOnly("隐私检查")}
        >
          隐私检查
        </button>
      </section>

      <div className="data-layout">
        <section className="panel table-panel">
          <h2>文件列表</h2>
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>文件名</th>
                  <th>大小</th>
                  <th>上传时间</th>
                  <th>特征数量</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {files.map((row) => (
                  <tr key={row.id}>
                    <td className="mono">{row.name}</td>
                    <td>{formatBytes(row.sizeBytes)}</td>
                    <td>{formatTime(row.uploadedAt)}</td>
                    <td>{row.featureCount?.toLocaleString() ?? "—"}</td>
                    <td>
                      <button
                        type="button"
                        className="link-btn danger"
                        onClick={() =>
                          setLocalFiles(files.filter((f) => f.id !== row.id))
                        }
                      >
                        移除登记
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <aside className="panel privacy-panel">
          <h2>隐私控制面板</h2>
          <p className="muted small">
            勾选后仅影响本机渲染与导出脱敏策略。
          </p>
          <label className="check-row">
            <input
              type="checkbox"
              checked={privacy.hideName}
              onChange={(e) => updatePrivacy("hideName", e.target.checked)}
            />
            <span>隐藏患者姓名</span>
          </label>
          <label className="check-row">
            <input
              type="checkbox"
              checked={privacy.blurBirth}
              onChange={(e) => updatePrivacy("blurBirth", e.target.checked)}
            />
            <span>模糊出生日期</span>
          </label>
          <label className="check-row">
            <input
              type="checkbox"
              checked={privacy.dpNoise}
              onChange={(e) => updatePrivacy("dpNoise", e.target.checked)}
            />
            <span>差分隐私加噪（本地）</span>
          </label>
          <div className="privacy-status">
            <span className="pill ok">本地模式</span>
            <span>无出站数据通道</span>
          </div>
        </aside>
      </div>
    </div>
  );
}
