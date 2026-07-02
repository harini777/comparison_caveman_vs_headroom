# 🪨 Caveman vs 📦 Headroom — Token Compression Arena

A live benchmarking dashboard that compares two LLM token-compression strategies — **Caveman** (output compression) and **Headroom** (input compression) — side-by-side against an uncompressed baseline.

## 📊 What It Does

Run the **same prompt** through three pipelines and compare token usage in real time:

| Pipeline | Strategy | How It Works |
|----------|----------|-------------|
| **Baseline** | No compression | Raw input in, normal response out |
| **Caveman** | Output compression | System prompt (from [SKILL.md](https://github.com/JuliusBrussee/caveman/blob/main/skills/caveman/SKILL.md)) enforces terse responses |
| **Headroom** | Input compression | [`headroom-ai`](https://pypi.org/project/headroom-ai/) SDK deduplicates & restructures context |

## ✨ Features

- **Demo mode** — Pre-built transaction fraud detection scenario (33 records, 3 suspicious)
- **Custom mode** — Enter your own prompt + optional context data (JSON, logs, etc.)
- **4 chart types** — Bar comparison, radar, waterfall, and donut breakdowns
- **Real implementations** — Actual Caveman SKILL.md prompt + real Headroom SDK (not simulated)
- **Dark "arena" theme** — Warm amber (Caveman) vs cool teal (Headroom) design

## 🚀 Quick Start

### 1. Clone & setup

```bash
git clone https://github.com/harini777/comparison_caveman_vs_headroom.git
cd comparison_caveman_vs_headroom
python -m venv venv
source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 2. Configure API key

```bash
cp .env.example .env
# Edit .env and add your Groq API key from https://console.groq.com
```

> **⚠️ Never commit `.env`** — it's in `.gitignore`.

### 3. Run

```bash
streamlit run app.py
```

## 📁 Project Structure

```
├── app.py              # Streamlit dashboard (interactive UI)
├── comparison.py       # CLI script (terminal output)
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
├── .gitignore          # Keeps secrets & artifacts out of git
└── README.md
```

## 🔑 API Key Security

- Keys loaded from **environment variables** (`GROQ_API_KEY`)
- `.env` is gitignored — never committed
- Also supports runtime input via password field

## 🛠️ Tech Stack

- **[Streamlit](https://streamlit.io/)** — Dashboard framework
- **[Plotly](https://plotly.com/python/)** — Interactive charts
- **[Groq](https://groq.com/)** — LLM inference (LLaMA 3.3 70B)
- **[Headroom](https://github.com/chopratejas/headroom)** — Input token compression SDK (`headroom-ai`)
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** — `.env` file loading

## 📖 How the Compression Strategies Work

### 🪨 [Caveman](https://github.com/JuliusBrussee/caveman) (by Julius Brussee)
Compresses **output** tokens using the actual system prompt from [Caveman's `SKILL.md`](https://github.com/JuliusBrussee/caveman/blob/main/skills/caveman/SKILL.md). The prompt instructs the LLM to drop articles, filler words, and pleasantries while keeping all technical substance intact.

### 📦 [Headroom](https://github.com/chopratejas/headroom) (by Headroom Labs)
Compresses **input** tokens using the **`headroom-ai`** Python SDK (`from headroom import compress`). Runs locally — no data egress — and intelligently deduplicates context before sending to the LLM.

### ⚡ Best Together
Caveman cuts output, Headroom cuts input. Combining both yields maximum token savings.
