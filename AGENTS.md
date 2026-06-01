# VLC Demodulation System - 项目文档

## 项目概述
VLC（可见光通信）智能解调系统，包含桌面端（PyQt5）和 Web 端。

---

## 技术栈

### 桌面端（已完成）
- PyQt5 桌面应用
- 中英文双语支持（core/i18n.py）
- 8 步操作指南（数据生成 → OFDM → LED → 信道 → 检测 → 解调 → AI → BER）

### Web 端（开发中）
| 层 | 技术 | 说明 |
|---|---|---|
| 后端 API | FastAPI + uvicorn | 封装 core/ 仿真引擎，提供 REST API |
| 仪表盘前端 | Jinja2 模板 + ECharts (CDN) | 仿真控制 + 交互图表，无需 Node.js |
| PPT 演示页 | reveal.js (CDN) | HTML 幻灯片，演示系统流程 |
| AI 能力 | DeepSeek API | 通过 openai 包调用（OpenAI 兼容接口） |
| PPT 导出 | python-pptx | 生成 .pptx 文件 |

### 关键设计决策
- **不用 Node.js/npm**：前端全部通过 CDN 引入，降低环境复杂度
- **不用 Streamlit**：虽然装了，但 reveal.js 做 PPT 效果更好，FastAPI 更灵活
- **DeepSeek 而非 OpenAI**：用户使用 DeepSeek API（兼容 OpenAI SDK）

---

## 已安装的 Python 包

```txt
# 桌面端
PyQt5>=5.15.0
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.4.0
scikit-learn>=1.0.0

# Web 后端
fastapi>=0.100.0
uvicorn>=0.20.0
Flask>=3.0.0
flask-cors>=4.0.0

# AI / DeepSeek
openai>=2.0.0          # DeepSeek 兼容 OpenAI SDK
httpx>=0.28.0
sse-starlette>=3.0.0

# 可视化
plotly>=6.0.0
streamlit>=1.50.0       # 备用快速原型

# PPT / 文档
python-pptx>=1.0.0
Pillow>=12.0.0
Jinja2>=3.0.0
Markdown>=3.0.0
```

---

## 项目结构

```
VLC_Demodulation_System/
├── main.py                  # 桌面端入口
├── core/                    # 仿真引擎（桌面+Web共用）
│   ├── vlc_simulator.py     # VLC 系统仿真
│   ├── ai_demodulator.py    # AI 解调器
│   ├── signal_processing.py # 信号处理
│   ├── channel.py           # 信道模型
│   ├── config_manager.py    # 配置管理
│   ├── i18n.py              # 中英文国际化
│   └── results_manager.py   # 结果管理
├── ui/                      # 桌面端 UI
│   ├── main_window.py       # 主窗口
│   ├── settings_tab.py      # 设置页
│   └── styles.py            # 样式
├── web/                     # 【新建】Web 端
│   ├── backend/
│   │   ├── app.py           # FastAPI 入口
│   │   └── api/             # API 路由
│   ├── frontend/
│   │   ├── templates/       # Jinja2 模板
│   │   ├── static/          # CSS/JS/图片
│   │   └── slides/          # reveal.js PPT 页
│   └── run.py               # 一键启动
├── results/                 # 仿真结果
├── config.json              # 配置文件
└── AGENTS.md                # 本文档
```

---

## 如何运行

### 桌面端
```bash
cd E:\codex.data\VLC_Demodulation_System
python main.py
```

### Web 端（开发中）
```bash
cd E:\codex.data\VLC_Demodulation_System\web
python run.py
# 访问 http://localhost:8000
```

---

## 环境配置

### VPN / 代理
- VPN 工具：E:\神器\ikuuu_vpn\iKuuuVPN.exe
- 代理地址：127.0.0.1:7890
- 使用方式（Python）：
```python
import os
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
```

### VS Code
- 路径：E:\codex-computer-use\tools\VSCode\Code.exe
- 快捷命令：E:\codex-computer-use\tools\VSCode\bin\code.cmd

### DeepSeek API
- 通过 openai 包调用，设置 base_url 指向 DeepSeek
```python
from openai import OpenAI
client = OpenAI(
    api_key="你的DeepSeek密钥",
    base_url="https://api.deepseek.com"
)
```

---

## 编码约定
- 所有文件 UTF-8 编码
- 中文文本直接用中文字符，不用 Unicode 转义
- i18n 翻译键用小写+下划线命名
- Web 前端优先 CDN，避免 npm 依赖
