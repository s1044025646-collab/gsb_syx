import { useState } from "react";
import { useTaskApplicationsMap } from "../hooks/useMedflStorage";
import { setTaskApplication } from "../utils/storage";

const TASKS = [
  {
    id: "t1",
    title: "XX 医院多中心皮肤病分类",
    algo: "FedAvg",
    roundCurrent: 45,
    roundTotal: 100,
    gpu: "建议 ≥ 12GB 显存（如 RTX 3080 / A4000）",
    format: "图像：PNG/JPEG 包 + CSV 标签；DICOM 需先转 NIfTI 或 PNG 切片。",
    desc: "多中心异构皮肤镜数据，标签空间统一为 8 类皮损。",
  },
  {
    id: "t2",
    title: "肺癌筛查 CT 弱监督检测",
    algo: "FedAvg + Scaffold",
    roundCurrent: 12,
    roundTotal: 80,
    gpu: "≥ 16GB 推荐（3D Patch 训练）",
    format: "NIfTI (.nii.gz) 体数据 + JSON 病灶框（可选）。",
    desc: "协调方提供全局 Anchor 模型，本地仅上传加密梯度。",
  },
  {
    id: "t3",
    title: "病理切片泛癌种迁移",
    algo: "FedProx",
    roundCurrent: 88,
    roundTotal: 120,
    gpu: "≥ 24GB（大切片编码器）",
    format: "WSI 需预先切块为 512×512 H5 特征或原图 Patch。",
    desc: "当前轮次较高，新节点将参与尾部微调阶段。",
  },
];

export default function TasksPage() {
  const applications = useTaskApplicationsMap();
  const [detailId, setDetailId] = useState(null);
  const [applyId, setApplyId] = useState(null);
  const [mapping, setMapping] = useState({
    local: "病历号",
    remote: "PatientID",
  });

  const detailTask = TASKS.find((t) => t.id === detailId);
  const applyTask = TASKS.find((t) => t.id === applyId);

  const submitApply = () => {
    if (!applyTask) return;
    setTaskApplication(applyTask.id, { ...mapping });
    setApplyId(null);
  };

  return (
    <div className="page tasks-page">
      <header className="page-head">
        <h1>联邦任务</h1>
        <p className="muted">
          浏览协调方发布的训练项目，查看资源与格式要求，申请加入并配置字段映射。
        </p>
      </header>

      <div className="task-grid">
        {TASKS.map((t) => (
          <article key={t.id} className="task-card">
            <div className="task-head">
              <h2>{t.title}</h2>
              <span className="algo-badge">{t.algo}</span>
            </div>
            <p className="muted small">{t.desc}</p>
            <div className="progress-block">
              <div className="progress-meta">
                进度 <strong>Round {t.roundCurrent}</strong> / {t.roundTotal}
              </div>
              <div className="progress-track">
                <div
                  className="progress-fill"
                  style={{
                    width: `${(t.roundCurrent / Math.max(1, t.roundTotal - 1)) * 100}%`,
                  }}
                />
              </div>
            </div>
            <div className="task-actions">
              <button
                type="button"
                className="btn secondary"
                onClick={() => setDetailId(t.id)}
              >
                详情
              </button>
              <button
                type="button"
                className="btn primary"
                onClick={() => {
                  setApplyId(t.id);
                  setMapping({
                    local: "病历号",
                    remote: "PatientID",
                  });
                }}
              >
                申请加入
              </button>
            </div>
            {applications[t.id] && (
              <p className="applied-tag">已提交映射 · 本地记录</p>
            )}
          </article>
        ))}
      </div>

      {detailTask && (
        <div className="modal-backdrop" role="dialog" aria-modal="true">
          <div className="modal">
            <h3>任务详情 · {detailTask.title}</h3>
            <dl className="detail-dl">
              <dt>算法</dt>
              <dd>{detailTask.algo}</dd>
              <dt>GPU 显存要求</dt>
              <dd>{detailTask.gpu}</dd>
              <dt>数据格式要求</dt>
              <dd>{detailTask.format}</dd>
            </dl>
            <button
              type="button"
              className="btn primary"
              onClick={() => setDetailId(null)}
            >
              关闭
            </button>
          </div>
        </div>
      )}

      {applyTask && (
        <div className="modal-backdrop" role="dialog" aria-modal="true">
          <div className="modal wide">
            <h3>字段映射 · {applyTask.title}</h3>
            <p className="muted small">
              将本院数据字典中的字段对应到任务方 schema（仅保存在本机 localStorage）。
            </p>
            <table className="mapping-table">
              <thead>
                <tr>
                  <th>本院字段</th>
                  <th />
                  <th>任务方字段</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <input
                      className="inp"
                      value={mapping.local}
                      onChange={(e) =>
                        setMapping((m) => ({ ...m, local: e.target.value }))
                      }
                    />
                  </td>
                  <td className="arrow-cell">⟶</td>
                  <td>
                    <input
                      className="inp"
                      value={mapping.remote}
                      onChange={(e) =>
                        setMapping((m) => ({ ...m, remote: e.target.value }))
                      }
                    />
                  </td>
                </tr>
                <tr>
                  <td>
                    <input className="inp" defaultValue="就诊科室" readOnly />
                  </td>
                  <td className="arrow-cell">⟶</td>
                  <td>
                    <input className="inp" defaultValue="Department" readOnly />
                  </td>
                </tr>
                <tr>
                  <td>
                    <input className="inp" defaultValue="检查日期" readOnly />
                  </td>
                  <td className="arrow-cell">⟶</td>
                  <td>
                    <input className="inp" defaultValue="StudyDate" readOnly />
                  </td>
                </tr>
              </tbody>
            </table>
            <div className="modal-actions">
              <button
                type="button"
                className="btn secondary"
                onClick={() => setApplyId(null)}
              >
                取消
              </button>
              <button type="button" className="btn primary" onClick={submitApply}>
                保存到本地
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
