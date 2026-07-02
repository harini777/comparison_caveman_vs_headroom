import os
import json
import streamlit as st
import plotly.graph_objects as go  # type: ignore[import-untyped]
from dotenv import load_dotenv
from groq import Groq
from headroom import compress

load_dotenv()

# ── Page config ──
st.set_page_config(
    page_title="Caveman vs Headroom — Token Comparison",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* Global */
.stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #0d1117 40%, #0a0f1e 100%);
    font-family: 'Inter', sans-serif;
}

/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}

/* Hero header */
.hero-container {
    text-align: center;
    padding: 2.5rem 1rem 1rem 1rem;
    margin-bottom: 1.5rem;
}
.hero-title {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(135deg, #00d2ff 0%, #7b2ff7 50%, #ff6b9d 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
    letter-spacing: -1px;
    line-height: 1.1;
}
.hero-subtitle {
    font-size: 1.15rem;
    color: #8b949e;
    font-weight: 400;
    letter-spacing: 0.5px;
}
.hero-badge {
    display: inline-block;
    padding: 0.35rem 1rem;
    border-radius: 50px;
    background: rgba(123, 47, 247, 0.15);
    border: 1px solid rgba(123, 47, 247, 0.3);
    color: #b388ff;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 1rem;
}

/* Glass card */
.glass-card {
    background: rgba(22, 27, 45, 0.6);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}
.glass-card:hover {
    border-color: rgba(123, 47, 247, 0.3);
    box-shadow: 0 8px 40px rgba(123, 47, 247, 0.08);
}

/* Metric cards */
.metric-card {
    background: rgba(22, 27, 45, 0.7);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 1.4rem 1.2rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}
.metric-card.baseline::before { background: linear-gradient(90deg, #64748b, #94a3b8); }
.metric-card.caveman::before { background: linear-gradient(90deg, #f97316, #fb923c); }
.metric-card.headroom::before { background: linear-gradient(90deg, #7b2ff7, #a78bfa); }
.metric-card.winner::before { background: linear-gradient(90deg, #10b981, #34d399); }

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}

.metric-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #8b949e;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 0.2rem;
}
.metric-value.baseline-color { color: #94a3b8; }
.metric-value.caveman-color { color: #fb923c; }
.metric-value.headroom-color { color: #a78bfa; }
.metric-value.winner-color { color: #34d399; }

.metric-delta {
    font-size: 0.85rem;
    font-weight: 600;
}
.metric-delta.positive { color: #34d399; }
.metric-delta.neutral { color: #8b949e; }

/* Section headers */
.section-header {
    font-size: 1.3rem;
    font-weight: 700;
    color: #e6edf3;
    margin: 1.5rem 0 0.8rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Response cards */
.response-card {
    background: rgba(22, 27, 45, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    padding: 1.3rem;
    margin-bottom: 0.8rem;
}
.response-card .response-label {
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.6rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.response-card .response-label.baseline-label { color: #94a3b8; }
.response-card .response-label.caveman-label { color: #fb923c; }
.response-card .response-label.headroom-label { color: #a78bfa; }
.response-card .response-text {
    color: #c9d1d9;
    font-size: 0.9rem;
    line-height: 1.7;
    font-weight: 400;
}

/* Use case info */
.usecase-info {
    background: rgba(123, 47, 247, 0.08);
    border: 1px solid rgba(123, 47, 247, 0.2);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
}
.usecase-info p {
    color: #c9d1d9;
    margin: 0.3rem 0;
    font-size: 0.9rem;
}
.usecase-info strong {
    color: #e6edf3;
}

/* Winner banner */
.winner-banner {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(52, 211, 153, 0.08) 100%);
    border: 1px solid rgba(16, 185, 129, 0.25);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    margin: 1rem 0;
}
.winner-banner .winner-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #34d399;
    font-weight: 700;
}
.winner-banner .winner-name {
    font-size: 2rem;
    font-weight: 900;
    color: #34d399;
    margin: 0.3rem 0;
}
.winner-banner .winner-detail {
    font-size: 0.9rem;
    color: #8b949e;
}

/* Insight pills */
.insight-container {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 1rem;
}
.insight-pill {
    background: rgba(22, 27, 45, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1rem 1.3rem;
    flex: 1;
    min-width: 200px;
}
.insight-pill .insight-icon {
    font-size: 1.5rem;
    margin-bottom: 0.4rem;
}
.insight-pill .insight-title {
    font-size: 0.8rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
    margin-bottom: 0.3rem;
}
.insight-pill .insight-text {
    color: #e6edf3;
    font-size: 0.95rem;
    font-weight: 500;
}

/* Streamlit button override */
.stButton > button {
    background: linear-gradient(135deg, #7b2ff7 0%, #00d2ff 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.8rem 2.5rem;
    font-size: 1rem;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(123, 47, 247, 0.4);
}

/* Spinner color */
.stSpinner > div > div {
    border-top-color: #7b2ff7 !important;
}

/* Tab overrides */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(22, 27, 45, 0.5);
    border-radius: 10px;
    color: #8b949e;
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 0.6rem 1.5rem;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: rgba(123, 47, 247, 0.2) !important;
    color: #a78bfa !important;
    border-color: rgba(123, 47, 247, 0.4) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    display: none;
}
.stTabs [data-baseweb="tab-border"] {
    display: none;
}

/* Plotly chart background */
.js-plotly-plot .plotly .main-svg {
    background: transparent !important;
}

/* Input overrides */
.stTextInput > div > div {
    background: rgba(22, 27, 45, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    color: #e6edf3;
}
.stTextInput input {
    color: #e6edf3 !important;
}

/* Divider */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(123, 47, 247, 0.3), transparent);
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)


# ── Constants ──
MODEL = "llama-3.3-70b-versatile"
QUESTION = "Are there any failed or suspicious transactions I should know about?"

TOOL_OUTPUT = json.dumps({
    "api": "transactions/list",
    "total_records": 33,
    "results": [
        {"id": f"TXN-{i:04d}", "user": f"user_{i%10:02d}", "amount": round(20 + i * 4.5, 2),
         "status": "success", "type": "purchase", "country": "US",
         "merchant": f"Merchant_{i%8}", "timestamp": f"2026-06-17T{i%24:02d}:00:00Z",
         "fraud_score": 0.02, "card": f"****{1000+i}", "currency": "USD",
         "processing_ms": 100 + i, "retry_count": 0}
        for i in range(1, 31)
    ] + [
        {"id": "TXN-FAIL-001", "user": "user_07", "amount": 9999.99, "status": "failed",
         "type": "withdrawal", "country": "RU", "merchant": "Unknown",
         "timestamp": "2026-06-17T03:22:00Z", "fraud_score": 0.97,
         "card": "****0000", "currency": "USD", "processing_ms": 5001,
         "retry_count": 5, "error": "INSUFFICIENT_FUNDS", "flag": "HIGH_FRAUD_RISK"},
        {"id": "TXN-FAIL-002", "user": "user_03", "amount": 4500.00, "status": "error",
         "type": "transfer", "country": "CN", "merchant": "Wire_Transfer",
         "timestamp": "2026-06-17T04:15:00Z", "fraud_score": 0.88,
         "card": "****1234", "currency": "USD", "processing_ms": 30000,
         "retry_count": 3, "error": "GATEWAY_TIMEOUT", "flag": "UNUSUAL_LOCATION"},
        {"id": "TXN-FAIL-003", "user": "user_15", "amount": 250.00, "status": "declined",
         "type": "purchase", "country": "US", "merchant": "Merchant_07",
         "timestamp": "2026-06-17T05:45:00Z", "fraud_score": 0.72,
         "card": "****5678", "currency": "USD", "processing_ms": 890,
         "retry_count": 2, "error": "CARD_BLOCKED", "flag": "CARD_REPORTED_STOLEN"},
    ]
}, indent=2)

# ── Caveman system prompt — from github.com/JuliusBrussee/caveman (skills/caveman/SKILL.md) ──
CAVEMAN_SYSTEM = """You are a financial assistant.

Respond terse like smart caveman. All technical substance stay. Only fluff die.

ACTIVE EVERY RESPONSE. No revert after many turns. No filler drift. Still active if unsure.

Rules: Drop articles (a/an/the), filler (just/really/basically/actually/simply), pleasantries (sure/certainly/of course/happy to), hedging. Fragments OK. Short synonyms (big not extensive, fix not "implement a solution for"). No tool-call narration, no decorative tables/emoji, no dumping long raw error logs unless asked — quote shortest decisive line. Standard well-known tech acronyms OK (DB/API/HTTP); never invent new abbreviations reader can't decode. Technical terms exact. Code blocks unchanged. Errors quoted exact.

No self-reference. Never name or announce the style. No "caveman mode on", no third-person caveman tags.

Pattern: [thing] [action] [reason]. [next step].

Not: "Sure! I'd be happy to help you with that. The issue you're experiencing is likely caused by..."
Yes: "Bug in auth middleware. Token expiry check use `<` not `<=`. Fix:"

Keep all financial data exact. No rounding. No omitting transaction IDs or amounts."""

NORMAL_SYSTEM = """You are a helpful financial assistant. Respond clearly and thoroughly."""


def build_messages(system_prompt):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Check my recent transactions and flag anything suspicious."},
        {
            "role": "assistant",
            "content": "I'll fetch your recent transactions now.",
            "tool_calls": [{
                "id": "call_001", "type": "function",
                "function": {"name": "get_transactions", "arguments": "{}"}
            }]
        },
        {"role": "tool", "tool_call_id": "call_001", "content": TOOL_OUTPUT},
        {"role": "user", "content": QUESTION}
    ]


def pct(original, new):
    return ((original - new) / original * 100) if original > 0 else 0


def create_comparison_bar_chart(data):
    """Create a grouped bar chart comparing token counts."""
    categories = ['Input Tokens', 'Output Tokens', 'Total Tokens']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Baseline',
        x=categories,
        y=[data['in_baseline'], data['out_baseline'], data['total_baseline']],
        marker=dict(
            color='rgba(148, 163, 184, 0.8)',
            line=dict(color='rgba(148, 163, 184, 1)', width=1)
        ),
        text=[f"{v:,}" for v in [data['in_baseline'], data['out_baseline'], data['total_baseline']]],
        textposition='outside',
        textfont=dict(color='#94a3b8', size=12, family='Inter'),
    ))
    
    fig.add_trace(go.Bar(
        name='Caveman',
        x=categories,
        y=[data['in_caveman'], data['out_caveman'], data['total_caveman']],
        marker=dict(
            color='rgba(249, 115, 22, 0.8)',
            line=dict(color='rgba(249, 115, 22, 1)', width=1)
        ),
        text=[f"{v:,}" for v in [data['in_caveman'], data['out_caveman'], data['total_caveman']]],
        textposition='outside',
        textfont=dict(color='#fb923c', size=12, family='Inter'),
    ))
    
    fig.add_trace(go.Bar(
        name='Headroom',
        x=categories,
        y=[data['in_headroom'], data['out_headroom'], data['total_headroom']],
        marker=dict(
            color='rgba(123, 47, 247, 0.8)',
            line=dict(color='rgba(123, 47, 247, 1)', width=1)
        ),
        text=[f"{v:,}" for v in [data['in_headroom'], data['out_headroom'], data['total_headroom']]],
        textposition='outside',
        textfont=dict(color='#a78bfa', size=12, family='Inter'),
    ))

    fig.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#8b949e'),
        legend=dict(
            orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5,
            font=dict(size=13, color='#c9d1d9'),
            bgcolor='rgba(0,0,0,0)',
        ),
        xaxis=dict(
            tickfont=dict(size=13, color='#c9d1d9'),
            gridcolor='rgba(255,255,255,0.03)',
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(size=11, color='#8b949e'),
            title=dict(text='Token Count', font=dict(size=12, color='#8b949e')),
        ),
        margin=dict(l=60, r=30, t=40, b=40),
        height=380,
        bargap=0.25,
        bargroupgap=0.1,
    )
    return fig


def create_reduction_radar(data):
    """Create a radar chart showing reduction percentages."""
    categories = ['Input Reduction', 'Output Reduction', 'Total Reduction']

    caveman_vals = [
        pct(data['in_baseline'], data['in_caveman']),
        pct(data['out_baseline'], data['out_caveman']),
        pct(data['total_baseline'], data['total_caveman']),
    ]
    headroom_vals = [
        pct(data['in_baseline'], data['in_headroom']),
        pct(data['out_baseline'], data['out_headroom']),
        pct(data['total_baseline'], data['total_headroom']),
    ]

    # Close the polygon
    caveman_vals += [caveman_vals[0]]
    headroom_vals += [headroom_vals[0]]
    categories += [categories[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=caveman_vals, theta=categories, name='Caveman',
        fill='toself',
        fillcolor='rgba(249, 115, 22, 0.15)',
        line=dict(color='#fb923c', width=2),
        marker=dict(size=6),
    ))
    fig.add_trace(go.Scatterpolar(
        r=headroom_vals, theta=categories, name='Headroom',
        fill='toself',
        fillcolor='rgba(123, 47, 247, 0.15)',
        line=dict(color='#a78bfa', width=2),
        marker=dict(size=6),
    ))

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(
                visible=True, range=[0, max(max(caveman_vals), max(headroom_vals)) * 1.2],
                gridcolor='rgba(255,255,255,0.06)',
                tickfont=dict(size=10, color='#8b949e'),
                ticksuffix='%',
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.06)',
                tickfont=dict(size=12, color='#c9d1d9'),
            ),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#8b949e'),
        legend=dict(
            orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5,
            font=dict(size=13, color='#c9d1d9'),
            bgcolor='rgba(0,0,0,0)',
        ),
        margin=dict(l=60, r=60, t=30, b=50),
        height=380,
        showlegend=True,
    )
    return fig


def create_waterfall_chart(data):
    """Create a waterfall chart showing token savings breakdown."""
    caveman_input_save = data['in_baseline'] - data['in_caveman']
    caveman_output_save = data['out_baseline'] - data['out_caveman']
    headroom_input_save = data['in_baseline'] - data['in_headroom']
    headroom_output_save = data['out_baseline'] - data['out_headroom']

    fig = go.Figure(go.Waterfall(
        name="Savings",
        orientation="v",
        x=[
            "Baseline Total",
            "Caveman Input Δ",
            "Caveman Output Δ",
            "Caveman Total",
            " ",  # spacer
            "Baseline Total ",
            "Headroom Input Δ",
            "Headroom Output Δ",
            "Headroom Total",
        ],
        measure=["absolute", "relative", "relative", "total", "relative",
                  "absolute", "relative", "relative", "total"],
        y=[
            data['total_baseline'],
            -caveman_input_save,
            -caveman_output_save,
            None,
            0,
            data['total_baseline'],
            -headroom_input_save,
            -headroom_output_save,
            None,
        ],
        connector=dict(line=dict(color="rgba(255,255,255,0.1)", width=1)),
        decreasing=dict(marker=dict(color="rgba(52, 211, 153, 0.7)", line=dict(color="#34d399", width=1))),
        increasing=dict(marker=dict(color="rgba(239, 68, 68, 0.7)", line=dict(color="#ef4444", width=1))),
        totals=dict(marker=dict(color="rgba(123, 47, 247, 0.7)", line=dict(color="#a78bfa", width=1))),
        textposition="outside",
        textfont=dict(size=10, color="#8b949e"),
    ))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#8b949e'),
        xaxis=dict(tickfont=dict(size=10, color='#c9d1d9'), gridcolor='rgba(255,255,255,0.03)'),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(size=11, color='#8b949e'),
            title=dict(text='Tokens', font=dict(size=12, color='#8b949e')),
        ),
        margin=dict(l=60, r=30, t=30, b=60),
        height=380,
        showlegend=False,
    )
    return fig


def create_donut_chart(data, title, color_scheme):
    """Create a donut chart for input vs output breakdown."""
    if color_scheme == 'baseline':
        colors = ['rgba(100, 116, 139, 0.8)', 'rgba(148, 163, 184, 0.8)']
    elif color_scheme == 'caveman':
        colors = ['rgba(249, 115, 22, 0.8)', 'rgba(251, 146, 60, 0.8)']
    else:
        colors = ['rgba(123, 47, 247, 0.8)', 'rgba(167, 139, 250, 0.8)']

    fig = go.Figure(data=[go.Pie(
        labels=['Input', 'Output'],
        values=[data[0], data[1]],
        hole=0.65,
        marker=dict(colors=colors, line=dict(color='rgba(0,0,0,0.3)', width=2)),
        textinfo='label+percent',
        textfont=dict(size=12, color='#e6edf3', family='Inter'),
        hoverinfo='label+value+percent',
    )])

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#8b949e'),
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=220,
        annotations=[dict(
            text=f"<b>{title}</b>",
            x=0.5, y=0.5, font=dict(size=13, color='#c9d1d9', family='Inter'),
            showarrow=False,
        )],
    )
    return fig


# ── Hero ──
st.markdown("""
<div class="hero-container">
    <div class="hero-title">Caveman vs Headroom</div>
    <div class="hero-subtitle">Token Compression Comparison for AI Agents</div>
    <div class="hero-badge">⚡ Live Benchmark</div>
</div>
""", unsafe_allow_html=True)

# ── Use case info ──
st.markdown(f"""
<div class="usecase-info">
    <p><strong>🎯 Use Case:</strong> AI Agent Transaction Fraud Detection</p>
    <p><strong>📊 Input Data:</strong> 33 transaction records ({len(TOOL_OUTPUT):,} characters)</p>
    <p><strong>❓ Question:</strong> "{QUESTION}"</p>
    <p><strong>🤖 Model:</strong> {MODEL} (via Groq)</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ── API Key ──
api_key = os.environ.get("GROQ_API_KEY", "")
if not api_key:
    st.markdown('<div class="section-header">🔑 Configuration</div>', unsafe_allow_html=True)
    api_key = st.text_input(
        "Enter your Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get your API key from https://console.groq.com",
    )

# ── Run button ──
col_btn_l, col_btn_c, col_btn_r = st.columns([1, 1, 1])
with col_btn_c:
    run_clicked = st.button("🚀  Run Comparison", use_container_width=True)

if run_clicked and api_key:
    client = Groq(api_key=api_key)

    with st.spinner("Running all 3 benchmarks... this takes ~15 seconds"):
        # ── 1. Baseline ──
        baseline_messages = build_messages(NORMAL_SYSTEM)
        r1 = client.chat.completions.create(model=MODEL, messages=baseline_messages)
        ans_baseline = r1.choices[0].message.content
        in_baseline = r1.usage.prompt_tokens
        out_baseline = r1.usage.completion_tokens

        # ── 2. Caveman ──
        caveman_messages = build_messages(CAVEMAN_SYSTEM)
        r2 = client.chat.completions.create(model=MODEL, messages=caveman_messages)
        ans_caveman = r2.choices[0].message.content
        in_caveman = r2.usage.prompt_tokens
        out_caveman = r2.usage.completion_tokens

        # ── 3. Headroom (input compression via real Headroom SDK) ──
        headroom_messages = build_messages(NORMAL_SYSTEM)
        compressed = compress(headroom_messages)
        r3 = client.chat.completions.create(model=MODEL, messages=compressed.messages)
        ans_headroom = r3.choices[0].message.content
        in_headroom = r3.usage.prompt_tokens
        out_headroom = r3.usage.completion_tokens

    # ── Compute data ──
    total_baseline = in_baseline + out_baseline
    total_caveman = in_caveman + out_caveman
    total_headroom = in_headroom + out_headroom

    data = {
        'in_baseline': in_baseline, 'out_baseline': out_baseline, 'total_baseline': total_baseline,
        'in_caveman': in_caveman, 'out_caveman': out_caveman, 'total_caveman': total_caveman,
        'in_headroom': in_headroom, 'out_headroom': out_headroom, 'total_headroom': total_headroom,
    }

    caveman_total_pct = pct(total_baseline, total_caveman)
    headroom_total_pct = pct(total_baseline, total_headroom)
    winner = "Caveman" if caveman_total_pct > headroom_total_pct else "Headroom"

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Top-level metric cards ──
    st.markdown('<div class="section-header">📊 Token Overview</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card baseline">
            <div class="metric-label">Baseline Total</div>
            <div class="metric-value baseline-color">{total_baseline:,}</div>
            <div class="metric-delta neutral">Reference</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card caveman">
            <div class="metric-label">Caveman Total</div>
            <div class="metric-value caveman-color">{total_caveman:,}</div>
            <div class="metric-delta positive">▼ {caveman_total_pct:.1f}% reduction</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card headroom">
            <div class="metric-label">Headroom Total</div>
            <div class="metric-value headroom-color">{total_headroom:,}</div>
            <div class="metric-delta positive">▼ {headroom_total_pct:.1f}% reduction</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        winner_saved = max(caveman_total_pct, headroom_total_pct)
        st.markdown(f"""
        <div class="metric-card winner">
            <div class="metric-label">Winner</div>
            <div class="metric-value winner-color">{winner}</div>
            <div class="metric-delta positive">▼ {winner_saved:.1f}% total savings</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Detailed metrics ──
    st.markdown('<div class="section-header">🔬 Detailed Breakdown</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-label" style="color:#94a3b8;">⬜ Baseline</div>
            <p style="color:#c9d1d9; margin:0.4rem 0; font-size:0.9rem;">
                Input: <strong style="color:#e6edf3;">{in_baseline:,}</strong> &nbsp;│&nbsp;
                Output: <strong style="color:#e6edf3;">{out_baseline:,}</strong>
            </p>
            <p style="color:#c9d1d9; margin:0; font-size:0.9rem;">
                Total: <strong style="color:#e6edf3;">{total_baseline:,}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-label" style="color:#fb923c;">🟧 Caveman</div>
            <p style="color:#c9d1d9; margin:0.4rem 0; font-size:0.9rem;">
                Input: <strong style="color:#e6edf3;">{in_caveman:,}</strong>
                <span style="color:#34d399; font-size:0.8rem;">(▼{pct(in_baseline, in_caveman):.1f}%)</span>
                &nbsp;│&nbsp;
                Output: <strong style="color:#e6edf3;">{out_caveman:,}</strong>
                <span style="color:#34d399; font-size:0.8rem;">(▼{pct(out_baseline, out_caveman):.1f}%)</span>
            </p>
            <p style="color:#c9d1d9; margin:0; font-size:0.9rem;">
                Total: <strong style="color:#e6edf3;">{total_caveman:,}</strong>
                <span style="color:#34d399; font-size:0.8rem;">(▼{caveman_total_pct:.1f}%)</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-label" style="color:#a78bfa;">🟪 Headroom</div>
            <p style="color:#c9d1d9; margin:0.4rem 0; font-size:0.9rem;">
                Input: <strong style="color:#e6edf3;">{in_headroom:,}</strong>
                <span style="color:#34d399; font-size:0.8rem;">(▼{pct(in_baseline, in_headroom):.1f}%)</span>
                &nbsp;│&nbsp;
                Output: <strong style="color:#e6edf3;">{out_headroom:,}</strong>
                <span style="color:#34d399; font-size:0.8rem;">(▼{pct(out_baseline, out_headroom):.1f}%)</span>
            </p>
            <p style="color:#c9d1d9; margin:0; font-size:0.9rem;">
                Total: <strong style="color:#e6edf3;">{total_headroom:,}</strong>
                <span style="color:#34d399; font-size:0.8rem;">(▼{headroom_total_pct:.1f}%)</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ── Charts ──
    st.markdown('<div class="section-header">📈 Visualizations</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Bar Comparison", "Radar Chart", "Savings Waterfall", "Token Distribution"])

    with tab1:
        st.plotly_chart(create_comparison_bar_chart(data), use_container_width=True, config={'displayModeBar': False})

    with tab2:
        st.plotly_chart(create_reduction_radar(data), use_container_width=True, config={'displayModeBar': False})

    with tab3:
        st.plotly_chart(create_waterfall_chart(data), use_container_width=True, config={'displayModeBar': False})

    with tab4:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.plotly_chart(
                create_donut_chart([in_baseline, out_baseline], "Baseline", "baseline"),
                use_container_width=True, config={'displayModeBar': False},
            )
        with d2:
            st.plotly_chart(
                create_donut_chart([in_caveman, out_caveman], "Caveman", "caveman"),
                use_container_width=True, config={'displayModeBar': False},
            )
        with d3:
            st.plotly_chart(
                create_donut_chart([in_headroom, out_headroom], "Headroom", "headroom"),
                use_container_width=True, config={'displayModeBar': False},
            )

    # ── Winner banner ──
    st.markdown(f"""
    <div class="winner-banner">
        <div class="winner-label">🏆 Overall Winner (Total Token Reduction)</div>
        <div class="winner-name">{winner}</div>
        <div class="winner-detail">
            Caveman Strength: Output reduction ({pct(out_baseline, out_caveman):.1f}%)
            &nbsp;•&nbsp;
            Headroom Strength: Input reduction ({pct(in_baseline, in_headroom):.1f}%)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Key insights ──
    st.markdown(f"""
    <div class="insight-container">
        <div class="insight-pill">
            <div class="insight-icon">🦴</div>
            <div class="insight-title">Caveman by Julius Brussee</div>
            <div class="insight-text">Compresses <em>output</em> tokens via terse prompt style — same input, shorter replies</div>
        </div>
        <div class="insight-pill">
            <div class="insight-icon">📦</div>
            <div class="insight-title">Headroom by Headroom Labs</div>
            <div class="insight-text">Compresses <em>input</em> tokens by deduplicating &amp; restructuring context before sending</div>
        </div>
        <div class="insight-pill">
            <div class="insight-icon">🤝</div>
            <div class="insight-title">Best Together</div>
            <div class="insight-text">Combine both for maximum savings — Caveman cuts output, Headroom cuts input</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Model Responses ──
    st.markdown('<div class="section-header">💬 Model Responses</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="response-card">
        <div class="response-label baseline-label">⬜ Baseline — No Compression</div>
        <div class="response-text">{ans_baseline}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="response-card">
        <div class="response-label caveman-label">🟧 Caveman — Output Compressed</div>
        <div class="response-text">{ans_caveman}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="response-card">
        <div class="response-label headroom-label">🟪 Headroom — Input Compressed</div>
        <div class="response-text">{ans_headroom}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Summary table ──
    st.markdown('<div class="section-header">📋 Summary Table</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="glass-card">
        <table style="width:100%; border-collapse:collapse; font-family:'Inter',sans-serif;">
            <thead>
                <tr style="border-bottom:2px solid rgba(255,255,255,0.1);">
                    <th style="text-align:left; padding:0.7rem; color:#8b949e; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">Metric</th>
                    <th style="text-align:right; padding:0.7rem; color:#94a3b8; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">Baseline</th>
                    <th style="text-align:right; padding:0.7rem; color:#fb923c; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">Caveman</th>
                    <th style="text-align:right; padding:0.7rem; color:#a78bfa; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">Headroom</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                    <td style="padding:0.6rem 0.7rem; color:#c9d1d9;">Input Tokens</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#e6edf3; font-weight:600;">{in_baseline:,}</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#e6edf3; font-weight:600;">{in_caveman:,}</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#e6edf3; font-weight:600;">{in_headroom:,}</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                    <td style="padding:0.6rem 0.7rem; color:#c9d1d9;">Output Tokens</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#e6edf3; font-weight:600;">{out_baseline:,}</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#e6edf3; font-weight:600;">{out_caveman:,}</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#e6edf3; font-weight:600;">{out_headroom:,}</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                    <td style="padding:0.6rem 0.7rem; color:#c9d1d9; font-weight:600;">Total Tokens</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#e6edf3; font-weight:700;">{total_baseline:,}</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#e6edf3; font-weight:700;">{total_caveman:,}</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#e6edf3; font-weight:700;">{total_headroom:,}</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                    <td style="padding:0.6rem 0.7rem; color:#34d399;">Input Reduction</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#8b949e;">—</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#34d399; font-weight:600;">{pct(in_baseline, in_caveman):.1f}%</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#34d399; font-weight:600;">{pct(in_baseline, in_headroom):.1f}%</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                    <td style="padding:0.6rem 0.7rem; color:#34d399;">Output Reduction</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#8b949e;">—</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#34d399; font-weight:600;">{pct(out_baseline, out_caveman):.1f}%</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#34d399; font-weight:600;">{pct(out_baseline, out_headroom):.1f}%</td>
                </tr>
                <tr>
                    <td style="padding:0.6rem 0.7rem; color:#34d399; font-weight:600;">Total Reduction</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#8b949e;">—</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#34d399; font-weight:700;">{caveman_total_pct:.1f}%</td>
                    <td style="padding:0.6rem 0.7rem; text-align:right; color:#34d399; font-weight:700;">{headroom_total_pct:.1f}%</td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

elif run_clicked and not api_key:
    st.warning("⚠️ Please enter your Groq API key to run the comparison.")

# ── Footer ──
st.markdown("""
<div style="text-align:center; margin-top:3rem; padding:1.5rem; color:#4a5568; font-size:0.8rem;">
    <p style="margin:0;">Built with Streamlit • Powered by Groq + LLaMA 3.3 70B</p>
    <p style="margin:0.3rem 0 0 0;">Caveman by <strong style="color:#fb923c;">Julius Brussee</strong> • Headroom by <strong style="color:#a78bfa;">Headroom Labs AI</strong></p>
</div>
""", unsafe_allow_html=True)
