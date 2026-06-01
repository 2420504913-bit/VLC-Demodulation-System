// VLC System App v7
const E=id=>document.getElementById(id);
let lang="en",simData=null,chatHistory=[],currentSub="waveform";
const charts={};

// Chinese translations - ONLY for Guide + API Docs
const ZH_GUIDE={
  title:"VLC 系统操作流程",
  sub:"8 个步骤，掌握完整 VLC 信号处理链路",
  steps:["数据源生成","OFDM 调制","LED 光发射","光信道传播","光电检测","OFDM 解调","AI 智能解码","BER 分析"],
  descs:["生成随机二进制数据作为 VLC 传输源。支持 512/1024/2048/4096 bits。QPSK 符号映射，作为 BER 真值参考。","正交频分复用对抗符号间干扰。64 点 FFT、48 数据子载波、16 点循环前缀。经 IFFT 到时域。","强度调制驱动蓝色 InGaN LED（450nm/100mW/120deg）。归一化偏置后在线性区工作，转为可见光。","自由空间视距信道：路径损耗、环境光干扰、散粒/热噪声。SNR 0-30dB 可调，叠加 AWGN。","PIN 光电二极管接收，响应度 0.5A/W。暗电流噪声建模，电信号放大采样后数字处理。","去除循环前缀后 FFT 转频域，提取数据子载波。最小距离硬判决输出含噪 QPSK 符号。","MLP 神经网络：5-64-32-4 架构。5000 样本多 SNR 条件训练，逐符号置信度评分。","解调比特 vs 原始比特，计算误码率 BER。四视图：波形/星座/眼图/BER。自动 0-24dB 扫描。"]
};

const EN_GUIDE={
  title:"VLC System Operation Guide",
  sub:"8 steps from data generation to BER analysis - master the complete VLC signal chain",
  steps:["Data Generation","OFDM Modulation","LED Transmission","Optical Channel","Photodetection","OFDM Demodulation","AI Decoding","BER Analysis"],
  descs:["Generates random binary data for VLC transmission. Configurable 512/1024/2048/4096 bits. QPSK symbol mapping.","OFDM combats inter-symbol interference. 64-FFT, 48 data subcarriers, 16-sample CP. IFFT to time domain.","Intensity modulation drives blue InGaN LED. Normalised to linear region for optical output.","Free-space LOS channel: path loss, shot/thermal noise. SNR 0-30dB, AWGN applied.","PIN photodiode receiver. Dark current noise modeled. Signal amplified and sampled.","Remove CP, FFT to frequency domain. Minimum-distance hard decision output.","MLP network: 5-64-32-4 architecture. 5000 samples trained across SNR conditions.","Demodulated vs original bits for BER. Four views: waveform, constellation, eye, BER."]
};

const ZH_API=[
  ["Simulation / 仿真接口","运行 VLC 仿真 / Run VLC simulation","BER 扫描 0-30dB / BER sweep","训练 AI 模型 / Train AI model"],
  ["AI / 智能分析 (DeepSeek)","AI 对话助手 / AI chat assistant","生成分析报告 / Generate report"],
  ["System / 系统管理","系统日志 / System logs","系统状态 / System status","保存设置 / Save settings"],
  ["Export / 导出","导出 PPTX 报告 / Export PPTX"]
];

const EN_API=[
  ["Simulation","Run VLC simulation","BER sweep 0-30dB","Train AI model"],
  ["AI (DeepSeek)","AI chat assistant","Generate analysis report"],
  ["System","System logs","System status","Save settings"],
  ["Export","Export PPTX report"]
];

function g(){return lang==="zh"?ZH_GUIDE:EN_GUIDE;}
function apiData(){return lang==="zh"?ZH_API:EN_API;}

document.addEventListener("DOMContentLoaded",async()=>{initMainTabs();initSubTabs();initAllCharts();await loadSettings();renderGuide();renderAPI();checkStatus();});

// ═══ Tabs ═══
function initMainTabs(){
  document.querySelectorAll("#mainNav .nav-tab").forEach(btn=>{btn.addEventListener("click",()=>switchToTab(btn.dataset.tab));});
}
function switchToTab(tabId){
  document.querySelectorAll("#mainNav .nav-tab").forEach(b=>b.classList.toggle("active",b.dataset.tab===tabId));
  document.querySelectorAll(".tab-content").forEach(t=>t.classList.remove("active"));
  const tab=E("tab-"+tabId); if(tab)tab.classList.add("active");
  E("subNav").style.display=tabId==="dashboard"?"flex":"none";
  if(tabId==="dashboard")setTimeout(resizeActiveChart,200);
  if(tabId==="slides")E("slidesScroll").scrollTop=0;
  if(tabId==="logs")refreshLogs();
  if(tabId==="settings")refreshDataList();
}

function initSubTabs(){
  document.querySelectorAll("#subNav .sub-tab").forEach(btn=>{btn.addEventListener("click",()=>{
    document.querySelectorAll("#subNav .sub-tab").forEach(b=>b.classList.remove("active"));
    btn.classList.add("active");currentSub=btn.dataset.sub;
    document.querySelectorAll(".sub-panel").forEach(p=>p.classList.remove("active"));
    const panel=E("panel-"+currentSub); if(panel)panel.classList.add("active");
    setTimeout(resizeActiveChart,200);
  });});
}

// ═══ Charts ═══
function initAllCharts(){
  ["chartWaveform","chartConstellation","chartEye","chartBER"].forEach(id=>{const el=E(id);if(el){if(charts[id])charts[id].dispose();charts[id]=echarts.init(el);}});
  window.addEventListener("resize",()=>resizeActiveChart());
}
function resizeActiveChart(){
  const c=charts["chart"+currentSub.charAt(0).toUpperCase()+currentSub.slice(1)];
  if(c)try{c.resize()}catch(e){}
}
function setChart(id,opt){const c=charts[id];if(c){c.setOption(opt,true);c.resize();}}

// ═══ Simulation ═══
async function runSimulation(){
  setStatus("running","Simulation running...");
  const p={data_length:+E("dataLength").value,snr_db:+E("snr").value,modulation:E("modulation").value,ai_model:E("aiModel").value};
  try{
    const r=await fetch("/api/simulate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(p)});
    const j=await r.json();
    if(j.success){simData=j.data;showResults(j.data);setTimeout(()=>updateAllCharts(),300);setStatus("ready","Simulation complete");}
    else setStatus("error",j.error);
  }catch(e){setStatus("error",e.message);}
}

async function runBERSweep(){
  setStatus("running","BER sweep running...");
  try{
    const r=await fetch("/api/ber_sweep",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({data_length:+E("dataLength").value,modulation:E("modulation").value,snr_db:20,ai_model:"None"})});
    const j=await r.json();
    if(j.success){
      if(!charts.chartBER){const el=E("chartBER");if(el)charts.chartBER=echarts.init(el);}
      setChart("chartBER",{title:{text:"BER vs SNR",left:"center",textStyle:{fontSize:14}},grid:{left:55,right:25,top:45,bottom:35},xAxis:{type:"category",data:j.data.snr_range,name:"SNR (dB)"},yAxis:{type:"log",name:"BER",min:1e-6},series:[{data:j.data.ber_values,type:"line",symbol:"circle",symbolSize:6,lineStyle:{color:"#d32f2f",width:2},itemStyle:{color:"#d32f2f"}}]});
      setStatus("ready","BER sweep complete");
    }
  }catch(e){setStatus("error",e.message);}
}

async function trainAI(){setStatus("ready","Model ready (pretrained)");}

function showResults(d){
  E("resultsDisplay").innerHTML='<div class=result-row><span>Modulation</span><strong>'+d.modulation+'</strong></div><div class=result-row><span>Data</span><strong>'+d.data_length+' bits</strong></div><div class=result-row><span>SNR</span><strong>'+d.snr_db+' dB</strong></div><div class=result-row><span>Errors</span><strong style=color:#d32f2f>'+d.errors+'</strong></div><div class=result-row><span>BER</span><strong style=color:'+(d.ber>0.1?'#d32f2f':'#2e7d32')+'>'+(typeof d.ber==='number'?d.ber.toExponential(4):d.ber)+'</strong></div><div class=result-row><span>Confidence</span><strong>'+(d.ai_confidence*100).toFixed(1)+'%</strong></div><div class=result-row><span>Time</span><strong>'+d.elapsed_ms+' ms</strong></div>';
}

function updateAllCharts(){
  if(!simData)return;
  const g={left:55,right:25,top:45,bottom:35};
  if(simData.waveform&&simData.waveform.length>0){
    if(!charts.chartWaveform){const el=E("chartWaveform");if(el)charts.chartWaveform=echarts.init(el);}
    setChart("chartWaveform",{title:{text:"Signal Waveform",left:"center",textStyle:{fontSize:14}},grid:g,xAxis:{type:"category",show:false},yAxis:{type:"value"},series:[{data:simData.waveform.slice(0,300),type:"line",symbol:"none",lineStyle:{color:"#4a7aaa",width:1},areaStyle:{color:"rgba(74,122,170,0.1)"}}]});
  }
  if(simData.constellation&&simData.constellation.length>0){
    if(!charts.chartConstellation){const el=E("chartConstellation");if(el)charts.chartConstellation=echarts.init(el);}
    let pts=simData.constellation,sd=[];
    if(Array.isArray(pts)){if(typeof pts[0]==="number"){for(let i=0;i<pts.length-1;i+=2)sd.push([pts[i],pts[i+1]]);}else if(Array.isArray(pts[0]))sd=pts;}
    if(sd.length>0)setChart("chartConstellation",{title:{text:"Constellation (Received Symbols)",left:"center",textStyle:{fontSize:14}},grid:g,xAxis:{type:"value",name:"I",splitLine:{show:false}},yAxis:{type:"value",name:"Q",splitLine:{show:false}},series:[{data:sd,type:"scatter",symbolSize:6,itemStyle:{color:"#4a7aaa",opacity:0.6}}]});
  }
  if(simData.eye_data&&simData.eye_data.length>0){
    if(!charts.chartEye){const el=E("chartEye");if(el)charts.chartEye=echarts.init(el);}
    setChart("chartEye",{title:{text:"Eye Diagram",left:"center",textStyle:{fontSize:14}},grid:g,xAxis:{type:"category",show:false},yAxis:{type:"value"},series:[{data:simData.eye_data.slice(0,200),type:"line",symbol:"none",lineStyle:{color:"#2e7d32",width:1}}]});
  }
  runBERSweep();
}

// ═══ Chat ═══
async function sendChat(){
  const inp=E("chatInput"),msg=inp.value.trim();if(!msg)return;inp.value="";
  const box=E("chatBox");box.innerHTML+='<div class=chat-msg user>'+msg+'</div>';box.scrollTop=box.scrollHeight;
  chatHistory.push({role:"user",content:msg});
  try{
    const r=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:msg,history:chatHistory.slice(0,-1)})});
    const j=await r.json();
    if(j.success){chatHistory.push({role:"assistant",content:j.reply});box.innerHTML+='<div class=chat-msg ai>'+j.reply.replace(/\n/g,"<br>")+'</div>';}
    else box.innerHTML+='<div class=chat-msg error>'+j.error+'</div>';
  }catch(e){box.innerHTML+='<div class=chat-msg error>Network error</div>';}
  box.scrollTop=box.scrollHeight;
}

async function generateReport(){
  E("reportContent").innerHTML="<p>AI analyzing...</p>";
  try{
    const r=await fetch("/api/generate_report",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({sim_data:simData||{}})});
    const j=await r.json();
    E("reportContent").innerHTML=j.success?'<div class=report-text>'+j.report.replace(/\n/g,"<br>")+'</div>':'<p style=color:#d32f2f>Error</p>';
  }catch(e){E("reportContent").innerHTML='<p style=color:#d32f2f>Network error</p>';}
}

async function exportPPTX(){setStatus("running","Exporting...");try{const r=await fetch("/api/export_pptx",{method:"POST"});const j=await r.json();setStatus("ready",j.success?"Exported: "+j.filename:"Failed");}catch(e){setStatus("error",e.message);}}

// ═══ Data Management ═══
async function saveCurrentData(){
  const name=prompt("Enter a name for this save:","Save "+(new Date().toLocaleString()));
  if(!name)return;
  try{
    const r=await fetch("/api/data/save",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name})});
    const j=await r.json();
    if(j.success){setStatus("ready","Data saved: "+j.name);refreshDataList();}
    else{setStatus("error",j.error||"Save failed");}
  }catch(e){setStatus("error",e.message);}
}

async function refreshDataList(){
  const el=E("dataList");if(!el)return;
  try{
    const r=await fetch("/api/data/list");const j=await r.json();
    const records=j.records||[];
    if(records.length===0){el.innerHTML="<p class=muted>No saved records</p>";return;}
    el.innerHTML=records.map(rec=>"<div class=data-row><div class=data-row-info><strong>"+rec.name+"</strong><span class=muted>"+rec.timestamp+" | "+rec.config.modulation+" SNR:"+rec.config.snr_db+"dB | BER:"+(rec.result.ber||"N/A")+"</span></div><button onclick=\"loadRecord("+rec.id+")\" class=\"btn btn-sm\">Load</button></div>").join("");
  }catch(e){el.innerHTML="<p class=muted>Failed to load records</p>";}
}

async function loadRecord(id){
  try{
    const r=await fetch("/api/data/load/"+id,{method:"POST"});
    const j=await r.json();
    if(j.success){
      simData=j.data;
      if(simData.modulation)E("modulation").value=simData.modulation;
      if(simData.data_length)E("dataLength").value=String(simData.data_length);
      if(simData.snr_db!=null){E("snr").value=simData.snr_db;E("snrValue").textContent=simData.snr_db;}
      updateCharts();
      updateResultsDisplay();
      switchToTab("dashboard");
      setStatus("ready","Loaded: "+simData.modulation+" SNR:"+simData.snr_db+"dB");
    }else{setStatus("error",j.error||"Load failed");}
  }catch(e){setStatus("error",e.message);}
}

function updateResultsDisplay(){
  const el=E("resultsDisplay");if(!el||!simData)return;
  el.innerHTML="<div class=result-row><span>Modulation</span><strong>"+simData.modulation+"</strong></div><div class=result-row><span>SNR</span><strong>"+simData.snr_db+" dB</strong></div><div class=result-row><span>BER</span><strong>"+simData.ber+"</strong></div><div class=result-row><span>AI Confidence</span><strong>"+(simData.ai_confidence||"N/A")+"%</strong></div><div class=result-row><span>Latency</span><strong>"+(simData.elapsed_ms||"N/A")+" ms</strong></div>";
}

// ═══ Logs ═══
async function refreshLogs(){
  try{
    const r=await fetch("/api/logs");const j=await r.json();
    const logs=j.logs||[];
    if(logs.length===0){E("logsDisplay").innerHTML='<p class=muted>No log entries yet. Run a simulation to generate logs.</p>';return;}
    E("logsDisplay").innerHTML='<table class=log-table><tr><th>Time</th><th>Action</th><th>Details</th><th>Status</th></tr>'+logs.reverse().map(l=>'<tr><td>'+l.timestamp+'</td><td>'+l.action+'</td><td>'+l.params+'</td><td class='+(l.status==="ok"?"log-ok":"log-err")+'>'+l.status+'</td></tr>').join("")+'</table>';
  }catch(e){E("logsDisplay").innerHTML='<p class=muted>Failed to load logs</p>';}
}
function clearLogs(){E("logsDisplay").innerHTML='<p class=muted>Logs cleared from display.</p>';}

// ═══ Status ═══
function setStatus(state,msg){const c={standby:"#999",running:"#ff9800",ready:"#4caf50",error:"#d32f2f"};E("statusText").innerHTML='<span style=color:'+(c[state]||"#999")+'>\u25cf</span> '+msg;}
async function checkStatus(){try{const r=await fetch("/api/status");const j=await r.json();E("apiStatus").textContent="API: Online | "+j.modulation;}catch(e){E("apiStatus").textContent="API: Offline";}}

// ═══ Language - ONLY affects Guide + API Docs ═══
function switchLang(l){
  lang=l;
  E("btnZh").classList.toggle("active",l==="zh");
  E("btnEn").classList.toggle("active",l==="en");
  renderGuide();
  renderAPI();
}

// ═══ Guide (bilingual) ═══
function renderGuide(){
  const c=E("guideSteps");if(!c)return;
  const gg=g(),n=["01","02","03","04","05","06","07","08"],k=["DATA","OFDM","LED","CH","PD","ODEM","AI","OUT"];
  // Update title
  const titleEl=document.querySelector("#tab-guide .guide-hero h1");
  if(titleEl)titleEl.textContent=gg.title;
  const subEl=document.querySelector("#tab-guide .guide-hero p");
  if(subEl)subEl.textContent=gg.sub;
  // Update steps
  c.innerHTML=gg.steps.map((x,i)=>'<div class=guide-card><div class=guide-card-hdr><span class=guide-num>'+n[i]+'</span><span class=guide-key>'+k[i]+'</span><span class=guide-title>'+x+'</span></div><p class=guide-desc>'+gg.descs[i]+'</p></div>').join("");
}

// ═══ API Docs (bilingual) ═══
function renderAPI(){
  const container=document.querySelector("#tab-api .api-container");
  if(!container)return;
  const ad=apiData();
  const methods=["POST","POST","POST","POST","POST","GET","GET","POST","POST","POST","GET","POST"];
  const paths=["/api/simulate","/api/ber_sweep","/api/train_ai","/api/chat","/api/generate_report","/api/logs","/api/status","/api/settings/save","/api/data/save","/api/data/list","/api/data/load/{id}","/api/export_pptx"];
  let html='<h1>VLC System API</h1><p>Base: <code>http://localhost:8000</code> | <a href="/docs" target="_blank">Swagger UI</a></p>';
  let mi=0;
  for(let s=0;s<ad.length;s++){
    html+='<h2>'+ad[s][0]+'</h2>';
    for(let i=1;i<ad[s].length;i++){
      html+='<div class=endpoint><span class="method '+(methods[mi]==="GET"?"get":"post")+'">'+methods[mi]+'</span><code>'+paths[mi]+'</code><p>'+ad[s][i]+'</p></div>';
      mi++;
    }
  }
  container.innerHTML=html;
}

// ═══ Theme ═══
function setTheme(th){document.body.className=document.body.className.replace(/theme-\w+/g,"")+" theme-"+th;E("thmLight").classList.toggle("active",th==="light");E("thmDark").classList.toggle("active",th==="dark");}
function setAccent(c){document.documentElement.style.setProperty("--accent",c);}
function setFontSize(sz){document.documentElement.style.fontSize=sz==="large"?"17px":"14px";E("fsMedium").classList.toggle("active",sz==="medium");E("fsLarge").classList.toggle("active",sz==="large");}

async function loadSettings(){
  try{const r=await fetch("/api/settings/load");const s=await r.json();if(s.lang){lang=s.lang;switchLang(lang);}if(s.theme)setTheme(s.theme);if(s.font_size)setFontSize(s.font_size);if(s.accent){E("accentColor").value=s.accent;setAccent(s.accent);}}catch(e){}
}
async function saveAllSettings(){
  const d={lang,theme:document.body.className.match(/theme-(\w+)/)?.[1]||"light",font_size:document.documentElement.style.fontSize==="17px"?"large":"medium",accent:E("accentColor").value};
  try{const r=await fetch("/api/settings/save",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(d)});const j=await r.json();const msg=E("settingsMsg");msg.textContent=j.success?"Saved!":"Error";setTimeout(()=>msg.textContent="",3000);}catch(e){E("settingsMsg").textContent="Failed";}
}
