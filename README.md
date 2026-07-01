# ⚡ Caveman vs Headroom — Token Compression Comparison

A live benchmarking tool that compares two LLM token-compression strategies — **Caveman** (output compression) and **Headroom** (input compression) — side-by-side against an uncompressed baseline.

## 📊 What It Does

This app sends the **same financial fraud-detection task** (33 transaction records → "flag suspicious ones") through three pipelines and compares the results:

| Pipeline | Strategy | What Gets Compressed |
|----------|----------|---------------------|
| **Baseline** | No compression | Nothing — raw JSON in, normal response out |
| **Caveman** | Output compression | System prompt enforces terse, caveman-style replies |
| **Headroom** | Input compression | Tool output (JSON) is deduplicated & restructured before sending |

The dashboard then visualizes token counts, reduction percentages, and the actual model responses across all three.

## 🖥️ Screenshots

The app features a dark-themed dashboard with:
- Token overview metric cards
- Bar charts, radar charts, waterfall charts, and donut charts
- Side-by-side model response comparison
- Winner determination based on total token savings

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/caveman-vs-headroom.git
cd caveman-vs-headroom
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

Copy the example env file and add your [Groq API key](https://console.groq.com):

```bash
cp .env.example .env
```

Then edit `.env`:

```
GROQ_API_KEY=gsk_your_actual_key_here
```

> **⚠️ Never commit your `.env` file.** It is already listed in `.gitignore`.

### 5. Run the app

**Streamlit dashboard (recommended):**

```bash
streamlit run app.py
```

**CLI version:**

```bash
python comparison.py
```

## 📁 Project Structure

```
├── app.py              # Streamlit dashboard (interactive UI)
├── comparison.py       # CLI script (terminal output)
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
├── .gitignore          # Keeps secrets & artifacts out of git
└── README.md           # This file
```

## 🔑 API Key Security

- API keys are loaded from **environment variables** (`GROQ_API_KEY`)
- The `.env` file is in `.gitignore` — it will **never** be committed
- `.env.example` is a safe template showing which variables are needed
- The Streamlit app also supports entering the key via a password input field at runtime

## 🛠️ Tech Stack

- **[Streamlit](https://streamlit.io/)** — Interactive web dashboard
- **[Plotly](https://plotly.com/python/)** — Charts and visualizations
- **[Groq](https://groq.com/)** — LLM inference (LLaMA 3.3 70B)
- **[Headroom](https://headroom.ai/)** — Input token compression SDK
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** — .env file loading

## 📖 How the Compression Strategies Work

### 🦴 Caveman (by Julius Brussee)
Compresses **output** tokens by using a system prompt that forces the LLM to respond in a terse, no-filler style. The input stays the same — only the generated response gets shorter.

### 📦 Headroom (by Headroom Labs)
Compresses **input** tokens by pre-processing the context (e.g., JSON tool output) before it reaches the LLM. Repetitive structures are deduplicated and converted to compact TSV format.

### 🤝 Best Together
The two strategies are complementary — Caveman cuts output, Headroom cuts input. Combining both yields maximum token savings.

## 📄 License

This project is for educational and research purposes.
