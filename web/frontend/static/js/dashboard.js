// VLC Dashboard - Main JS

let currentLang = "zh";
let chatHistory = [];
let simData = null;

// ── 初始化 ──
document.addEventListener("DOMContentLoaded", () => {
  initCharts();
  checkStatus();
});

// ── 图表初始化 ──
const charts = {};
function initCharts() {
  const ids = ["chartWaveform", "chartConstellation", "chartEye", "chartBER"];
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) charts[id] = echarts.init(el);
  });
  window.addEventListener("resize", () => Object.values(charts).forEach(c => c.resize()));
}

// ── 仿真 ──
async function runSimulation() {
  updateStatus("running", "仿真运行中...");
  const payload = {
    data_length: parseInt(document.getElementById("dataLength").value),
    snr_db: parseFloat(document.getElementById("snr").value),
    modulation: document.getElementById("modulation").value,
    ai_model: document.getElementById("aiModel").value,
  };
  try {
    const res = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const json = await res.json();
    if (json.success) {
      simData = json.data;
      displayResults(json.data);
      updateCharts();
      updateStatus("ready", "仿真完成");
    } else {
      updateStatus("error", "错误: " + json.error);
    }
  } catch (e) {
    updateStatus("error", "网络错误: " + e.message);
  }
}

async function runBERSweep() {
  updateStatus("running", "BER 扫描中...");
  const payload = {
    data_length: parseInt(document.getElementById("dataLength").value),
    modulation: document.getElementById("modulation").value,
    snr_db: 20, ai_model: "None",
  };
  try {
    const res = await fetch("/api/ber_sweep", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const json = await res.json();
    if (json.success) {
      updateBERChart(json.data.snr_range, json.data.ber_values);
      updateStatus("ready", "BER 扫描完成");
    }
  } catch (e) {
    updateStatus("error", "扫描失败: " + e.message);
  }
}

async function trainAI() {
  updateStatus("running", "AI 训练中...");
  try {
    const res = await fetch("/api/train_ai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ modulation: document.getElementById("modulation").value, data_length: 1024, snr_db: 20, ai_model: document.getElementById("aiModel").value }),
    });
    const json = await res.json();
    if (json.success) {
      updateStatus("ready", `AI 训练完成 | 准确率: ${(json.data.accuracy * 100).toFixed(1)}% | ${json.data.elapsed_ms}ms`);
    }
  } catch (e) {
    updateStatus("error", "训练失败: " + e.message);
  }
}

// ── 结果展示 ──
function displayResults(d) {
  document.getElementById("resultsDisplay").innerHTML = `
    <div class="result-row"><span>调制:</span><strong>${d.modulation}</strong></div>
    <div class="result-row"><span>数据长度:</span><strong>${d.data_length} bits</strong></div>
    <div class="result-row"><span>SNR:</span><strong>${d.snr_db} dB</strong></div>
    <div class="result-row"><span>发送比特:</span><strong>${d.tx_bits}</strong></div>
    <div class="result-row"><span>错误数:</span><strong style="color:#d32f2f">${d.errors}</strong></div>
    <div class="result-row"><span>BER:</span><strong style="color:${d.ber>0.1?'#d32f2f':'#2e7d32'}">${typeof d.ber==='number'?d.ber.toExponential(4):d.ber}</strong></div>
    <div class="result-row"><span>AI 置信度:</span><strong>${(d.ai_confidence*100).toFixed(1)}%</strong></div>
    <div class="result-row"><span>耗时:</span><strong>${d.elapsed_ms} ms</strong></div>
  `;
}

// ── 图表更新 ──
function updateCharts() {
  if (!simData) return;
  // 波形
  if (simData.waveform && charts.chartWaveform) {
    charts.chartWaveform.setOption({
      title: { text: "信号波形", left: "center", textStyle: { fontSize: 12 } },
      xAxis: { type: "category", show: false },
      yAxis: { type: "value" },
      series: [{ data: simData.waveform.slice(0, 300), type: "line", symbol: "none", lineStyle: { color: "#4a7aaa", width: 1 }, areaStyle: { color: "rgba(74,122,170,0.1)" } }],
      grid: { left: 40, right: 20, top: 30, bottom: 20 },
    });
  }
  // 星座图
  if (simData.constellation && charts.chartConstellation) {
    let pts = simData.constellation;
    let scatterData = [];
    if (Array.isArray(pts) && pts.length > 0) {
      if (typeof pts[0] === "number") {
        for (let i = 0; i < pts.length - 1; i += 2) scatterData.push([pts[i], pts[i + 1]]);
      } else {
        scatterData = pts;
      }
    }
    charts.chartConstellation.setOption({
      title: { text: "星座图", left: "center", textStyle: { fontSize: 12 } },
      xAxis: { type: "value", name: "I", splitLine: { show: false } },
      yAxis: { type: "value", name: "Q", splitLine: { show: false } },
      series: [{ data: scatterData.slice(0, 500), type: "scatter", symbolSize: 6, itemStyle: { color: "#4a7aaa", opacity: 0.6 } }],
      grid: { left: 45, right: 20, top: 30, bottom: 30 },
    });
  }
  // 眼图
  if (simData.eye_data && charts.chartEye) {
    charts.chartEye.setOption({
      title: { text: "眼图", left: "center", textStyle: { fontSize: 12 } },
      xAxis: { type: "category", show: false },
      yAxis: { type: "value" },
      series: [{ data: simData.eye_data.slice(0, 200), type: "line", symbol: "none", lineStyle: { color: "#2e7d32", width: 1 } }],
      grid: { left: 40, right: 20, top: 30, bottom: 20 },
    });
  }
  // BER
  runBERSweep();
}

function updateBERChart(snrRange, berValues) {
  if (!charts.chartBER) return;
  charts.chartBER.setOption({
    title: { text: "BER vs SNR", left: "center", textStyle: { fontSize: 12 } },
    xAxis: { type: "category", data: snrRange, name: "SNR (dB)" },
    yAxis: { type: "log", name: "BER", min: 1e-6 },
    series: [{ data: berValues, type: "line", symbol: "circle", symbolSize: 6, lineStyle: { color: "#d32f2f", width: 2 }, itemStyle: { color: "#d32f2f" } }],
    grid: { left: 55, right: 20, top: 30, bottom: 30 },
  });
}

// ── AI 聊天 ──
async function sendChat() {
  const input = document.getElementById("chatInput");
  const msg = input.value.trim();
  if (!msg) return;
  input.value = "";

  const box = document.getElementById("chatBox");
  box.innerHTML += `<div class="chat-msg user">👤 ${msg}</div>`;
  box.scrollTop = box.scrollHeight;

  chatHistory.push({ role: "user", content: msg });

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, history: chatHistory.slice(0, -1) }),
    });
    const json = await res.json();
    if (json.success) {
      chatHistory.push({ role: "assistant", content: json.reply });
      box.innerHTML += `<div class="chat-msg ai">🤖 ${json.reply.replace(/\n/g, "<br>")}</div>`;
    } else {
      box.innerHTML += `<div class="chat-msg error">❌ ${json.error}</div>`;
    }
    box.scrollTop = box.scrollHeight;
  } catch (e) {
    box.innerHTML += `<div class="chat-msg error">❌ 网络错误</div>`;
  }
}

async function generateReport() {
  const box = document.getElementById("reportContent");
  box.innerHTML = "<p>⏳ DeepSeek AI 正在分析...</p>";
  try {
    const res = await fetch("/api/generate_report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sim_data: simData || {} }),
    });
    const json = await res.json();
    if (json.success) {
      box.innerHTML = `<div class="report-text">${json.report.replace(/\n/g, "<br>")}</div>`;
    } else {
      box.innerHTML = `<p style="color:#d32f2f">❌ ${json.error}</p>`;
    }
  } catch (e) {
    box.innerHTML = `<p style="color:#d32f2f">❌ 网络错误</p>`;
  }
}

async function exportPPTX() {
  updateStatus("running", "导出 PPTX...");
  try {
    const res = await fetch("/api/export_pptx", { method: "POST" });
    const json = await res.json();
    if (json.success) {
      updateStatus("ready", `PPTX 已导出: ${json.filename}`);
    } else {
      updateStatus("error", "导出失败: " + json.error);
    }
  } catch (e) {
    updateStatus("error", "导出失败");
  }
}

// ── 语言切换 ──
async function toggleLang() {
  currentLang = currentLang === "zh" ? "en" : "zh";
  document.getElementById("btnLang").textContent = currentLang === "zh" ? "🌐 中文" : "🌐 English";
  try {
    await fetch("/api/language", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lang: currentLang }),
    });
  } catch (e) {}
}

// ── 状态 ──
function updateStatus(state, msg) {
  const el = document.getElementById("statusText");
  const icons = { standby: "●", running: "◉", ready: "●", error: "●" };
  const colors = { standby: "#999", running: "#ff9800", ready: "#4caf50", error: "#d32f2f" };
  el.innerHTML = `<span style="color:${colors[state]||'#999'}">${icons[state]||'●'}</span> ${msg}`;
}

async function checkStatus() {
  try {
    const res = await fetch("/api/status");
    const json = await res.json();
    document.getElementById("apiStatus").textContent = `API: 在线 | ${json.modulation} | AI: ${json.ai_trained?'已训练':'未训练'}`;
  } catch (e) {
    document.getElementById("apiStatus").textContent = "API: 离线";
  }
}
