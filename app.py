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
    page_title="Caveman vs Headroom — Token Compression Arena",
    page_icon="🪨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Design System: Warm Caveman amber vs Cool Headroom teal on dark slate ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

/* Global */
.stApp {
    background: #0f1419;
    font-family: 'Space Grotesk', sans-serif;
    color: #c5cdd8;
}

/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}

/* ── Arena Header ── */
.arena-header {
    text-align: center;
    padding: 2rem 1rem 0.5rem;
    position: relative;
}
.arena-header::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 60%;
    height: 2px;
    background: linear-gradient(90deg, transparent, #e8a838 30%, #0ea5e9 70%, transparent);
}
.arena-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.6rem;
    font-weight: 700;
    letter-spacing: -1.5px;
    margin-bottom: 0.2rem;
    line-height: 1.1;
}
.arena-title .cave { color: #e8a838; }
.arena-title .vs { color: #475569; font-weight: 400; font-size: 1.8rem; }
.arena-title .head { color: #22d3ee; }
.arena-sub {
    color: #64748b;
    font-size: 1rem;
    font-weight: 400;
    letter-spacing: 0.3px;
}
.arena-tags {
    display: flex;
    justify-content: center;
    gap: 0.6rem;
    margin-top: 0.8rem;
}
.arena-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    padding: 0.25rem 0.7rem;
    border-radius: 4px;
    letter-spacing: 0.5px;
}
.arena-tag.cave-tag {
    background: rgba(232, 168, 56, 0.1);
    border: 1px solid rgba(232, 168, 56, 0.3);
    color: #e8a838;
}
.arena-tag.head-tag {
    background: rgba(14, 165, 233, 0.1);
    border: 1px solid rgba(14, 165, 233, 0.3);
    color: #22d3ee;
}
.arena-tag.live-tag {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #34d399;
}

/* ── Dividers ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(100, 116, 139, 0.3), transparent);
    margin: 1.2rem 0;
}
.divider-warm {
    background: linear-gradient(90deg, transparent, rgba(232, 168, 56, 0.3), rgba(14, 165, 233, 0.3), transparent);
}

/* ── Cards ── */
.slate-card {
    background: #1a1f2e;
    border: 1px solid #2a3040;
    border-radius: 12px;
    padding: 1.3rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s ease;
}
.slate-card:hover {
    border-color: #3a4050;
}

/* ── Metric Cards ── */
.m-card {
    background: #1a1f2e;
    border: 1px solid #2a3040;
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.m-card:hover {
    transform: translateY(-3px);
    border-color: #3a4050;
}
.m-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
}
.m-card.c-base::after { background: #475569; }
.m-card.c-cave::after { background: #e8a838; }
.m-card.c-head::after { background: #0ea5e9; }
.m-card.c-win::after { background: #10b981; }

.m-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #64748b;
    font-weight: 600;
    margin-bottom: 0.4rem;
}
.m-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -1px;
    margin-bottom: 0.15rem;
}
.m-value.v-base { color: #94a3b8; }
.m-value.v-cave { color: #e8a838; }
.m-value.v-head { color: #22d3ee; }
.m-value.v-win { color: #34d399; }

.m-delta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
}
.m-delta.pos { color: #34d399; }
.m-delta.neu { color: #64748b; }

/* ── Section headers ── */
.sec-head {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: #e2e8f0;
    margin: 1.2rem 0 0.6rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    letter-spacing: -0.3px;
}

/* ── Response cards ── */
.resp-card {
    background: #1a1f2e;
    border: 1px solid #2a3040;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 0.6rem;
}
.resp-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.5rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #2a3040;
}
.resp-label.l-base { color: #94a3b8; }
.resp-label.l-cave { color: #e8a838; }
.resp-label.l-head { color: #22d3ee; }
.resp-text {
    color: #c5cdd8;
    font-size: 0.88rem;
    line-height: 1.7;
    font-weight: 400;
}

/* ── Config panel ── */
.config-panel {
    background: #161b26;
    border: 1px solid #2a3040;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}
.config-panel p {
    color: #94a3b8;
    margin: 0.25rem 0;
    font-size: 0.88rem;
}
.config-panel strong { color: #e2e8f0; }

/* ── Winner banner ── */
.win-banner {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(52, 211, 153, 0.04) 100%);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 12px;
    padding: 1.3rem;
    text-align: center;
    margin: 0.8rem 0;
}
.win-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #34d399;
    font-weight: 600;
}
.win-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #34d399;
    margin: 0.2rem 0;
}
.win-detail {
    font-size: 0.85rem;
    color: #64748b;
}

/* ── Insight cards ── */
.insight-row {
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
    margin-top: 0.8rem;
}
.insight-item {
    background: #1a1f2e;
    border: 1px solid #2a3040;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    flex: 1;
    min-width: 200px;
}
.insight-item .i-icon { font-size: 1.3rem; margin-bottom: 0.3rem; }
.insight-item .i-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
    margin-bottom: 0.2rem;
}
.insight-item .i-text {
    color: #e2e8f0;
    font-size: 0.88rem;
    font-weight: 500;
}

/* ── Streamlit overrides ── */
.stButton > button {
    background: linear-gradient(135deg, #e8a838 0%, #0ea5e9 100%);
    color: #0f1419;
    border: none;
    border-radius: 8px;
    padding: 0.7rem 2rem;
    font-size: 0.95rem;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
    letter-spacing: 0.3px;
    transition: all 0.2s ease;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(232, 168, 56, 0.25);
}

.stSpinner > div > div { border-top-color: #e8a838 !important; }

.stTabs [data-baseweb="tab-list"] { gap: 6px; background: transparent; }
.stTabs [data-baseweb="tab"] {
    background: #1a1f2e;
    border-radius: 8px;
    color: #64748b;
    border: 1px solid #2a3040;
    padding: 0.5rem 1.2rem;
    font-weight: 600;
    font-family: 'Space Grotesk', sans-serif;
}
.stTabs [aria-selected="true"] {
    background: rgba(232, 168, 56, 0.12) !important;
    color: #e8a838 !important;
    border-color: rgba(232, 168, 56, 0.3) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }
.stTabs [data-baseweb="tab-border"] { display: none; }

.js-plotly-plot .plotly .main-svg { background: transparent !important; }

.stTextInput > div > div, .stTextArea > div > div {
    background: #1a1f2e;
    border: 1px solid #2a3040;
    border-radius: 8px;
    color: #e2e8f0;
}
.stTextInput input, .stTextArea textarea { color: #e2e8f0 !important; }

.stRadio > div { gap: 0.5rem; }
.stRadio label { color: #c5cdd8 !important; }

.stSelectbox > div > div {
    background: #1a1f2e;
    border: 1px solid #2a3040;
    color: #e2e8f0;
}
</style>
""", unsafe_allow_html=True)


# ── Constants ──
MODEL = "llama-3.3-70b-versatile"

DEMO_QUESTION = "Are there any failed or suspicious transactions I should know about?"

DEMO_TOOL_OUTPUT = json.dumps({
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
CAVEMAN_PROMPT_CORE = """Respond terse like smart caveman. All technical substance stay. Only fluff die.

ACTIVE EVERY RESPONSE. No revert after many turns. No filler drift. Still active if unsure.

Rules: Drop articles (a/an/the), filler (just/really/basically/actually/simply), pleasantries (sure/certainly/of course/happy to), hedging. Fragments OK. Short synonyms (big not extensive, fix not "implement a solution for"). No tool-call narration, no decorative tables/emoji, no dumping long raw error logs unless asked — quote shortest decisive line. Standard well-known tech acronyms OK (DB/API/HTTP); never invent new abbreviations reader can't decode. Technical terms exact. Code blocks unchanged. Errors quoted exact.

No self-reference. Never name or announce the style. No "caveman mode on", no third-person caveman tags.

Pattern: [thing] [action] [reason]. [next step].

Not: "Sure! I'd be happy to help you with that. The issue you're experiencing is likely caused by..."
Yes: "Bug in auth middleware. Token expiry check use `<` not `<=`. Fix:"

Keep all data exact. No rounding. No omitting IDs or amounts."""

NORMAL_SYSTEM = """You are a helpful assistant. Respond clearly and thoroughly."""


def build_messages(system_prompt, user_query, tool_output, question):
    """Build messages with tool-call simulation for context-heavy comparison."""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query},
        {
            "role": "assistant",
            "content": "I'll fetch the relevant data now.",
            "tool_calls": [{
                "id": "call_001", "type": "function",
                "function": {"name": "get_data", "arguments": "{}"}
            }]
        },
        {"role": "tool", "tool_call_id": "call_001", "content": tool_output},
        {"role": "user", "content": question}
    ]


def build_simple_messages(system_prompt, user_input):
    """Build simple messages for custom user input (no tool calls)."""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]


def pct(original, new):
    return ((original - new) / original * 100) if original > 0 else 0


def create_comparison_bar_chart(data):
    categories = ['Input Tokens', 'Output Tokens', 'Total Tokens']
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Baseline', x=categories,
        y=[data['in_baseline'], data['out_baseline'], data['total_baseline']],
        marker=dict(color='rgba(148, 163, 184, 0.7)', line=dict(color='#94a3b8', width=1)),
        text=[f"{v:,}" for v in [data['in_baseline'], data['out_baseline'], data['total_baseline']]],
        textposition='outside', textfont=dict(color='#94a3b8', size=11, family='JetBrains Mono'),
    ))
    fig.add_trace(go.Bar(
        name='Caveman', x=categories,
        y=[data['in_caveman'], data['out_caveman'], data['total_caveman']],
        marker=dict(color='rgba(232, 168, 56, 0.7)', line=dict(color='#e8a838', width=1)),
        text=[f"{v:,}" for v in [data['in_caveman'], data['out_caveman'], data['total_caveman']]],
        textposition='outside', textfont=dict(color='#e8a838', size=11, family='JetBrains Mono'),
    ))
    fig.add_trace(go.Bar(
        name='Headroom', x=categories,
        y=[data['in_headroom'], data['out_headroom'], data['total_headroom']],
        marker=dict(color='rgba(14, 165, 233, 0.7)', line=dict(color='#0ea5e9', width=1)),
        text=[f"{v:,}" for v in [data['in_headroom'], data['out_headroom'], data['total_headroom']]],
        textposition='outside', textfont=dict(color='#22d3ee', size=11, family='JetBrains Mono'),
    ))

    fig.update_layout(
        barmode='group', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Space Grotesk', color='#64748b'),
        legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5,
                    font=dict(size=12, color='#c5cdd8'), bgcolor='rgba(0,0,0,0)'),
        xaxis=dict(tickfont=dict(size=12, color='#c5cdd8'), gridcolor='rgba(255,255,255,0.03)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickfont=dict(size=10, color='#64748b'),
                   title=dict(text='Token Count', font=dict(size=11, color='#64748b'))),
        margin=dict(l=50, r=20, t=35, b=35), height=370, bargap=0.2, bargroupgap=0.08,
    )
    return fig


def create_reduction_radar(data):
    categories = ['Input Reduction', 'Output Reduction', 'Total Reduction']
    cave_vals = [pct(data['in_baseline'], data['in_caveman']),
                 pct(data['out_baseline'], data['out_caveman']),
                 pct(data['total_baseline'], data['total_caveman'])]
    head_vals = [pct(data['in_baseline'], data['in_headroom']),
                 pct(data['out_baseline'], data['out_headroom']),
                 pct(data['total_baseline'], data['total_headroom'])]
    cave_vals += [cave_vals[0]]
    head_vals += [head_vals[0]]
    categories += [categories[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=cave_vals, theta=categories, name='Caveman', fill='toself',
        fillcolor='rgba(232, 168, 56, 0.1)', line=dict(color='#e8a838', width=2), marker=dict(size=5),
    ))
    fig.add_trace(go.Scatterpolar(
        r=head_vals, theta=categories, name='Headroom', fill='toself',
        fillcolor='rgba(14, 165, 233, 0.1)', line=dict(color='#22d3ee', width=2), marker=dict(size=5),
    ))

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0, max(max(cave_vals), max(head_vals)) * 1.2],
                            gridcolor='rgba(255,255,255,0.05)', tickfont=dict(size=9, color='#64748b'), ticksuffix='%'),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickfont=dict(size=11, color='#c5cdd8')),
        ),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(family='Space Grotesk', color='#64748b'),
        legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5,
                    font=dict(size=12, color='#c5cdd8'), bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=50, r=50, t=25, b=45), height=370, showlegend=True,
    )
    return fig


def create_waterfall_chart(data):
    cave_in_save = data['in_baseline'] - data['in_caveman']
    cave_out_save = data['out_baseline'] - data['out_caveman']
    head_in_save = data['in_baseline'] - data['in_headroom']
    head_out_save = data['out_baseline'] - data['out_headroom']

    fig = go.Figure(go.Waterfall(
        name="Savings", orientation="v",
        x=["Baseline", "Cave Input Δ", "Cave Output Δ", "Caveman Total",
           " ", "Baseline ", "Head Input Δ", "Head Output Δ", "Headroom Total"],
        measure=["absolute", "relative", "relative", "total", "relative",
                 "absolute", "relative", "relative", "total"],
        y=[data['total_baseline'], -cave_in_save, -cave_out_save, None, 0,
           data['total_baseline'], -head_in_save, -head_out_save, None],
        connector=dict(line=dict(color="rgba(255,255,255,0.06)", width=1)),
        decreasing=dict(marker=dict(color="rgba(52, 211, 153, 0.6)", line=dict(color="#34d399", width=1))),
        increasing=dict(marker=dict(color="rgba(239, 68, 68, 0.6)", line=dict(color="#ef4444", width=1))),
        totals=dict(marker=dict(color="rgba(100, 116, 139, 0.5)", line=dict(color="#94a3b8", width=1))),
        textposition="outside", textfont=dict(size=9, color="#64748b"),
    ))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Space Grotesk', color='#64748b'),
        xaxis=dict(tickfont=dict(size=9, color='#c5cdd8'), gridcolor='rgba(255,255,255,0.03)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickfont=dict(size=10, color='#64748b'),
                   title=dict(text='Tokens', font=dict(size=11, color='#64748b'))),
        margin=dict(l=50, r=20, t=25, b=55), height=370, showlegend=False,
    )
    return fig


def create_donut_chart(values, title, scheme):
    colors = {
        'baseline': ['rgba(100, 116, 139, 0.7)', 'rgba(148, 163, 184, 0.7)'],
        'caveman': ['rgba(232, 168, 56, 0.7)', 'rgba(212, 118, 78, 0.7)'],
        'headroom': ['rgba(14, 165, 233, 0.7)', 'rgba(34, 211, 238, 0.7)'],
    }[scheme]

    fig = go.Figure(data=[go.Pie(
        labels=['Input', 'Output'], values=values, hole=0.65,
        marker=dict(colors=colors, line=dict(color='rgba(0,0,0,0.3)', width=2)),
        textinfo='label+percent', textfont=dict(size=11, color='#e2e8f0', family='Space Grotesk'),
        hoverinfo='label+value+percent',
    )])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Space Grotesk', color='#64748b'), showlegend=False,
        margin=dict(l=8, r=8, t=8, b=8), height=200,
        annotations=[dict(text=f"<b>{title}</b>", x=0.5, y=0.5,
                          font=dict(size=12, color='#c5cdd8', family='Space Grotesk'), showarrow=False)],
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HEADER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div class="arena-header">
    <div class="arena-title">
        <span class="cave">🪨 Caveman</span>
        <span class="vs">&nbsp;vs&nbsp;</span>
        <span class="head">Headroom 📦</span>
    </div>
    <div class="arena-sub">Token Compression Arena — Which strategy saves more?</div>
    <div class="arena-tags">
        <span class="arena-tag cave-tag">OUTPUT COMPRESSION</span>
        <span class="arena-tag head-tag">INPUT COMPRESSION</span>
        <span class="arena-tag live-tag">LIVE BENCHMARK</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider divider-warm"></div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  INPUT MODE SELECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
mode = st.radio(
    "Choose input mode",
    ["🎯 Demo — Transaction Fraud Detection", "✏️ Custom — Your Own Prompt"],
    horizontal=True,
    label_visibility="collapsed",
)

is_custom = mode.startswith("✏️")

if not is_custom:
    # ── Demo mode info ──
    st.markdown(f"""
    <div class="config-panel">
        <p><strong>🎯 Use Case:</strong> AI Agent Transaction Fraud Detection</p>
        <p><strong>📊 Input Data:</strong> 33 transaction records ({len(DEMO_TOOL_OUTPUT):,} chars of JSON)</p>
        <p><strong>❓ Question:</strong> "{DEMO_QUESTION}"</p>
        <p><strong>🤖 Model:</strong> {MODEL} via Groq</p>
    </div>
    """, unsafe_allow_html=True)

    tool_output = DEMO_TOOL_OUTPUT
    user_query = "Check my recent transactions and flag anything suspicious."
    question = DEMO_QUESTION
    use_tool_calls = True
else:
    # ── Custom mode inputs ──
    st.markdown('<div class="sec-head">✏️ Enter Your Prompt</div>', unsafe_allow_html=True)

    custom_input = st.text_area(
        "Your prompt or question",
        placeholder="e.g., Summarize the key points of this document...\n\nPaste any context, data, or text you want the LLM to process here.",
        height=150,
        label_visibility="collapsed",
    )

    col_ctx_label, _ = st.columns([1, 3])
    with col_ctx_label:
        has_context = st.checkbox("I have additional context data (JSON, logs, etc.)", value=False)

    if has_context:
        custom_context = st.text_area(
            "Context data",
            placeholder='Paste JSON, logs, or any data the LLM should analyze alongside your prompt...',
            height=200,
            label_visibility="collapsed",
        )
    else:
        custom_context = ""

    # Set variables for custom mode
    if has_context and custom_context.strip():
        tool_output = custom_context.strip()
        user_query = custom_input.strip() if custom_input.strip() else "Analyze the following data."
        question = custom_input.strip() if custom_input.strip() else "What are the key findings?"
        use_tool_calls = True
    else:
        tool_output = ""
        user_query = custom_input.strip() if custom_input.strip() else ""
        question = ""
        use_tool_calls = False

    st.markdown(f"""
    <div class="config-panel">
        <p><strong>🤖 Model:</strong> {MODEL} via Groq</p>
        <p><strong>📝 Mode:</strong> {"With context data" if use_tool_calls else "Direct prompt"}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  API KEY + RUN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
api_key = os.environ.get("GROQ_API_KEY", "")
if not api_key:
    st.markdown('<div class="sec-head">🔑 Configuration</div>', unsafe_allow_html=True)
    api_key = st.text_input(
        "Groq API Key", type="password", placeholder="gsk_...",
        help="Get your API key from https://console.groq.com",
    )

_, col_btn, _ = st.columns([1, 1, 1])
with col_btn:
    run_clicked = st.button("🚀  Run Comparison", use_container_width=True)

# ── Validate custom input ──
if run_clicked and is_custom and not user_query:
    st.warning("⚠️ Please enter a prompt before running.")
    st.stop()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BENCHMARK EXECUTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if run_clicked and api_key:
    client = Groq(api_key=api_key)

    # Build the Caveman system prompt
    caveman_system = f"{NORMAL_SYSTEM}\n\n{CAVEMAN_PROMPT_CORE}"

    with st.spinner("Running 3 benchmarks... ~15 seconds"):

        if use_tool_calls:
            # ── Mode: With tool output / context data ──
            # 1. Baseline
            baseline_msgs = build_messages(NORMAL_SYSTEM, user_query, tool_output, question)
            r1 = client.chat.completions.create(model=MODEL, messages=baseline_msgs)

            # 2. Caveman
            caveman_msgs = build_messages(caveman_system, user_query, tool_output, question)
            r2 = client.chat.completions.create(model=MODEL, messages=caveman_msgs)

            # 3. Headroom
            headroom_msgs = build_messages(NORMAL_SYSTEM, user_query, tool_output, question)
            compressed = compress(headroom_msgs)
            r3 = client.chat.completions.create(model=MODEL, messages=compressed.messages)
        else:
            # ── Mode: Simple prompt (no tool calls) ──
            # 1. Baseline
            baseline_msgs = build_simple_messages(NORMAL_SYSTEM, user_query)
            r1 = client.chat.completions.create(model=MODEL, messages=baseline_msgs)

            # 2. Caveman
            caveman_msgs = build_simple_messages(caveman_system, user_query)
            r2 = client.chat.completions.create(model=MODEL, messages=caveman_msgs)

            # 3. Headroom
            headroom_msgs = build_simple_messages(NORMAL_SYSTEM, user_query)
            compressed = compress(headroom_msgs)
            r3 = client.chat.completions.create(model=MODEL, messages=compressed.messages)

        ans_baseline = r1.choices[0].message.content
        in_baseline = r1.usage.prompt_tokens
        out_baseline = r1.usage.completion_tokens

        ans_caveman = r2.choices[0].message.content
        in_caveman = r2.usage.prompt_tokens
        out_caveman = r2.usage.completion_tokens

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

    st.markdown('<div class="divider divider-warm"></div>', unsafe_allow_html=True)


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  RESULTS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown('<div class="sec-head">📊 Token Overview</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="m-card c-base">
            <div class="m-label">Baseline Total</div>
            <div class="m-value v-base">{total_baseline:,}</div>
            <div class="m-delta neu">Reference</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="m-card c-cave">
            <div class="m-label">Caveman Total</div>
            <div class="m-value v-cave">{total_caveman:,}</div>
            <div class="m-delta pos">▼ {caveman_total_pct:.1f}%</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="m-card c-head">
            <div class="m-label">Headroom Total</div>
            <div class="m-value v-head">{total_headroom:,}</div>
            <div class="m-delta pos">▼ {headroom_total_pct:.1f}%</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        winner_pct = max(caveman_total_pct, headroom_total_pct)
        st.markdown(f"""
        <div class="m-card c-win">
            <div class="m-label">Winner</div>
            <div class="m-value v-win">{winner}</div>
            <div class="m-delta pos">▼ {winner_pct:.1f}% savings</div>
        </div>""", unsafe_allow_html=True)


    # ── Detailed breakdown ──
    st.markdown('<div class="sec-head">🔬 Detailed Breakdown</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown(f"""
        <div class="slate-card">
            <div class="m-label" style="color:#94a3b8;">⬜ Baseline</div>
            <p style="color:#c5cdd8; margin:0.3rem 0; font-size:0.88rem;">
                Input: <strong style="color:#e2e8f0;">{in_baseline:,}</strong> &nbsp;│&nbsp;
                Output: <strong style="color:#e2e8f0;">{out_baseline:,}</strong>
            </p>
            <p style="color:#c5cdd8; margin:0; font-size:0.88rem;">
                Total: <strong style="color:#e2e8f0;">{total_baseline:,}</strong>
            </p>
        </div>""", unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="slate-card">
            <div class="m-label" style="color:#e8a838;">🪨 Caveman</div>
            <p style="color:#c5cdd8; margin:0.3rem 0; font-size:0.88rem;">
                Input: <strong style="color:#e2e8f0;">{in_caveman:,}</strong>
                <span style="color:#34d399; font-size:0.75rem;">(▼{pct(in_baseline, in_caveman):.1f}%)</span>
                &nbsp;│&nbsp;
                Output: <strong style="color:#e2e8f0;">{out_caveman:,}</strong>
                <span style="color:#34d399; font-size:0.75rem;">(▼{pct(out_baseline, out_caveman):.1f}%)</span>
            </p>
            <p style="color:#c5cdd8; margin:0; font-size:0.88rem;">
                Total: <strong style="color:#e2e8f0;">{total_caveman:,}</strong>
                <span style="color:#34d399; font-size:0.75rem;">(▼{caveman_total_pct:.1f}%)</span>
            </p>
        </div>""", unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="slate-card">
            <div class="m-label" style="color:#22d3ee;">📦 Headroom</div>
            <p style="color:#c5cdd8; margin:0.3rem 0; font-size:0.88rem;">
                Input: <strong style="color:#e2e8f0;">{in_headroom:,}</strong>
                <span style="color:#34d399; font-size:0.75rem;">(▼{pct(in_baseline, in_headroom):.1f}%)</span>
                &nbsp;│&nbsp;
                Output: <strong style="color:#e2e8f0;">{out_headroom:,}</strong>
                <span style="color:#34d399; font-size:0.75rem;">(▼{pct(out_baseline, out_headroom):.1f}%)</span>
            </p>
            <p style="color:#c5cdd8; margin:0; font-size:0.88rem;">
                Total: <strong style="color:#e2e8f0;">{total_headroom:,}</strong>
                <span style="color:#34d399; font-size:0.75rem;">(▼{headroom_total_pct:.1f}%)</span>
            </p>
        </div>""", unsafe_allow_html=True)


    # ── Charts ──
    st.markdown('<div class="sec-head">📈 Visualizations</div>', unsafe_allow_html=True)

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
            st.plotly_chart(create_donut_chart([in_baseline, out_baseline], "Baseline", "baseline"),
                            use_container_width=True, config={'displayModeBar': False})
        with d2:
            st.plotly_chart(create_donut_chart([in_caveman, out_caveman], "Caveman", "caveman"),
                            use_container_width=True, config={'displayModeBar': False})
        with d3:
            st.plotly_chart(create_donut_chart([in_headroom, out_headroom], "Headroom", "headroom"),
                            use_container_width=True, config={'displayModeBar': False})


    # ── Winner banner ──
    st.markdown(f"""
    <div class="win-banner">
        <div class="win-label">🏆 Overall Winner — Total Token Reduction</div>
        <div class="win-name">{winner}</div>
        <div class="win-detail">
            Caveman: output ▼{pct(out_baseline, out_caveman):.1f}%
            &nbsp;•&nbsp;
            Headroom: input ▼{pct(in_baseline, in_headroom):.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)


    # ── Insights ──
    st.markdown(f"""
    <div class="insight-row">
        <div class="insight-item">
            <div class="i-icon">🪨</div>
            <div class="i-title">Caveman — JuliusBrussee/caveman</div>
            <div class="i-text">Compresses <em>output</em> via system prompt from SKILL.md — same input, shorter replies</div>
        </div>
        <div class="insight-item">
            <div class="i-icon">📦</div>
            <div class="i-title">Headroom — headroom-ai SDK</div>
            <div class="i-text">Compresses <em>input</em> by deduplicating & restructuring context before sending</div>
        </div>
        <div class="insight-item">
            <div class="i-icon">⚡</div>
            <div class="i-title">Best Together</div>
            <div class="i-text">Combine both — Caveman cuts output, Headroom cuts input. Maximum savings.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


    # ── Model Responses ──
    st.markdown('<div class="sec-head">💬 Model Responses</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="resp-card">
        <div class="resp-label l-base">⬜ Baseline — No Compression</div>
        <div class="resp-text">{ans_baseline}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="resp-card">
        <div class="resp-label l-cave">🪨 Caveman — Output Compressed</div>
        <div class="resp-text">{ans_caveman}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="resp-card">
        <div class="resp-label l-head">📦 Headroom — Input Compressed</div>
        <div class="resp-text">{ans_headroom}</div>
    </div>
    """, unsafe_allow_html=True)


    # ── Summary table ──
    st.markdown('<div class="sec-head">📋 Summary</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="slate-card">
        <table style="width:100%; border-collapse:collapse; font-family:'JetBrains Mono',monospace; font-size:0.82rem;">
            <thead>
                <tr style="border-bottom:2px solid #2a3040;">
                    <th style="text-align:left; padding:0.6rem; color:#64748b; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px;">Metric</th>
                    <th style="text-align:right; padding:0.6rem; color:#94a3b8; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px;">Baseline</th>
                    <th style="text-align:right; padding:0.6rem; color:#e8a838; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px;">Caveman</th>
                    <th style="text-align:right; padding:0.6rem; color:#22d3ee; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px;">Headroom</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom:1px solid #1f2535;">
                    <td style="padding:0.5rem 0.6rem; color:#c5cdd8;">Input Tokens</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#e2e8f0; font-weight:600;">{in_baseline:,}</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#e2e8f0; font-weight:600;">{in_caveman:,}</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#e2e8f0; font-weight:600;">{in_headroom:,}</td>
                </tr>
                <tr style="border-bottom:1px solid #1f2535;">
                    <td style="padding:0.5rem 0.6rem; color:#c5cdd8;">Output Tokens</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#e2e8f0; font-weight:600;">{out_baseline:,}</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#e2e8f0; font-weight:600;">{out_caveman:,}</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#e2e8f0; font-weight:600;">{out_headroom:,}</td>
                </tr>
                <tr style="border-bottom:1px solid #1f2535;">
                    <td style="padding:0.5rem 0.6rem; color:#c5cdd8; font-weight:600;">Total Tokens</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#e2e8f0; font-weight:700;">{total_baseline:,}</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#e2e8f0; font-weight:700;">{total_caveman:,}</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#e2e8f0; font-weight:700;">{total_headroom:,}</td>
                </tr>
                <tr style="border-bottom:1px solid #1f2535;">
                    <td style="padding:0.5rem 0.6rem; color:#34d399;">Input Reduction</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#475569;">—</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#34d399; font-weight:600;">{pct(in_baseline, in_caveman):.1f}%</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#34d399; font-weight:600;">{pct(in_baseline, in_headroom):.1f}%</td>
                </tr>
                <tr style="border-bottom:1px solid #1f2535;">
                    <td style="padding:0.5rem 0.6rem; color:#34d399;">Output Reduction</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#475569;">—</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#34d399; font-weight:600;">{pct(out_baseline, out_caveman):.1f}%</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#34d399; font-weight:600;">{pct(out_baseline, out_headroom):.1f}%</td>
                </tr>
                <tr>
                    <td style="padding:0.5rem 0.6rem; color:#34d399; font-weight:600;">Total Reduction</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#475569;">—</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#34d399; font-weight:700;">{caveman_total_pct:.1f}%</td>
                    <td style="padding:0.5rem 0.6rem; text-align:right; color:#34d399; font-weight:700;">{headroom_total_pct:.1f}%</td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

elif run_clicked and not api_key:
    st.warning("⚠️ Please enter your Groq API key to run the comparison.")


# ── Footer ──
st.markdown("""
<div style="text-align:center; margin-top:2.5rem; padding:1.2rem; color:#475569; font-size:0.75rem; font-family:'JetBrains Mono',monospace;">
    <p style="margin:0;">Powered by Groq + LLaMA 3.3 70B</p>
    <p style="margin:0.2rem 0 0 0;">
        Caveman by <strong style="color:#e8a838;">JuliusBrussee/caveman</strong>
        &nbsp;•&nbsp;
        Headroom by <strong style="color:#22d3ee;">headroom-ai</strong>
    </p>
</div>
""", unsafe_allow_html=True)
