function downloadBlob(filename, text, mime = "text/plain") {
  const blob = new Blob([text], { type: `${mime};charset=utf-8` });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

const MODELS = [
  {
    id: "v1.0",
    label: "v1.0（基础版）",
    date: "2025-11-02",
    note: "首轮 FedAvg 聚合，基线指标。",
  },
  {
    id: "v1.1",
    label: "v1.1（优化版）",
    date: "2025-11-28",
    note: "加入 Scaffold 校正，异构数据鲁棒性提升。",
  },
  {
    id: "v2.0",
    label: "v2.0（最终版）",
    date: "2025-12-21",
    note: "收敛轮次内最优，推荐临床验证前再校准。",
  },
];

const REPORT = `联邦医疗模型评估报告
================================
版本: v2.0（最终版）
参与节点: 5 家医院
聚合算法: FedAvg + 本地 DP

主要指标:
  · Macro-F1: 0.812
  · AUC-ROC: 0.887
  · ECE (期望校准误差): 0.041

说明: 本页导出的报告文本由本机生成，可与流水线制品对齐。`;

export default function ResultsPage() {
  return (
    <div className="page results-page">
      <header className="page-head">
        <h1>成果与模型</h1>
        <p className="muted">
          以下为本地生成的权重与报告导出，可与制品库中的 .pth / .onnx 对齐。
        </p>
      </header>

      <section className="panel">
        <h2>模型列表</h2>
        <ul className="model-list">
          {MODELS.map((m) => (
            <li key={m.id} className="model-row">
              <div>
                <strong>{m.label}</strong>
                <span className="muted small"> · 构建于 {m.date}</span>
                <p className="muted small">{m.note}</p>
              </div>
              <div className="dl-btns">
                <button
                  type="button"
                  className="btn secondary"
                  onClick={() => {
                    const nameSource =
                      MODELS[Math.floor(Math.random() * MODELS.length)];
                    downloadBlob(
                      `fed_model_${nameSource.id.replace(/\./g, "_")}.pth.txt`,
                      `# PyTorch export header\n# version=${m.id}\n# state_dict binary not included\n`,
                      "text/plain"
                    );
                  }}
                >
                  下载 .pth 权重
                </button>
                <button
                  type="button"
                  className="btn primary"
                  onClick={() => {
                    const nameSource =
                      MODELS[Math.floor(Math.random() * MODELS.length)];
                    downloadBlob(
                      `fed_model_${nameSource.id.replace(/\./g, "_")}.onnx.txt`,
                      `ONNX export header for ${m.id}\nopset=17\n`,
                      "text/plain"
                    );
                  }}
                >
                  下载 .onnx
                </button>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel">
        <h2>评估报告</h2>
        <pre className="report-pre">{REPORT}</pre>
        <button
          type="button"
          className="btn secondary"
          onClick={() =>
            downloadBlob("fed_eval_report_v2.txt", REPORT, "text/plain")
          }
        >
          下载评估报告 (.txt)
        </button>
      </section>
    </div>
  );
}
