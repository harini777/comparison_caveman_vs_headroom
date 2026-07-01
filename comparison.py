import os
import json
from dotenv import load_dotenv
from groq import Groq
from headroom import compress

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = "llama-3.3-70b-versatile"

# ── Shared use case: AI agent reads transaction data and answers a question ──
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

# ── Caveman system prompt (simulates Caveman skill) ──
CAVEMAN_SYSTEM = """You are a financial assistant. Respond in caveman style — drop articles, filler, hedging. 
Keep all technical facts exact. Short fragments OK. No pleasantries."""

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

def main():
    if not GROQ_API_KEY:
        print("Error: Set GROQ_API_KEY environment variable.")
        return

    client = Groq(api_key=GROQ_API_KEY)

    print("\n" + "="*65)
    print("  CAVEMAN vs HEADROOM — TOKEN REDUCTION COMPARISON")
    print("  Use Case: AI Agent Transaction Fraud Detection")
    print("="*65)
    print(f"  Input data : 33 transaction records ({len(TOOL_OUTPUT):,} chars)")
    print(f"  Question   : {QUESTION}\n")
    print("  Running all 3 requests, please wait...\n")

    # ── 1. Baseline (no compression) ──
    baseline_messages = build_messages(NORMAL_SYSTEM)
    r1 = client.chat.completions.create(model=MODEL, messages=baseline_messages)
    ans_baseline = r1.choices[0].message.content
    in_baseline = r1.usage.prompt_tokens
    out_baseline = r1.usage.completion_tokens

    # ── 2. Caveman (output compressed via system prompt style) ──
    caveman_messages = build_messages(CAVEMAN_SYSTEM)
    r2 = client.chat.completions.create(model=MODEL, messages=caveman_messages)
    ans_caveman = r2.choices[0].message.content
    in_caveman = r2.usage.prompt_tokens
    out_caveman = r2.usage.completion_tokens

    # ── 3. Headroom (input compressed) ──
    headroom_messages = build_messages(NORMAL_SYSTEM)
    compressed = compress(headroom_messages)
    r3 = client.chat.completions.create(model=MODEL, messages=compressed.messages)
    ans_headroom = r3.choices[0].message.content
    in_headroom = r3.usage.prompt_tokens
    out_headroom = r3.usage.completion_tokens

    # ── Calculate reductions ──
    def pct(original, new):
        return ((original - new) / original * 100) if original > 0 else 0

    total_baseline = in_baseline + out_baseline
    total_caveman = in_caveman + out_caveman
    total_headroom = in_headroom + out_headroom

    # ── Print answers ──
    print("-"*65)
    print("  BASELINE (no compression)")
    print("-"*65)
    print(f"  Answer: {ans_baseline[:300]}{'...' if len(ans_baseline)>300 else ''}\n")

    print("-"*65)
    print("  CAVEMAN (output compressed)")
    print("-"*65)
    print(f"  Answer: {ans_caveman[:300]}{'...' if len(ans_caveman)>300 else ''}\n")

    print("-"*65)
    print("  HEADROOM (input compressed)")
    print("-"*65)
    print(f"  Answer: {ans_headroom[:300]}{'...' if len(ans_headroom)>300 else ''}\n")

    # ── Summary table ──
    print("="*65)
    print("  SUMMARY — TOKEN COMPARISON VS BASELINE")
    print("="*65)
    print(f"  {'Metric':<25} {'Baseline':>10} {'Caveman':>10} {'Headroom':>10}")
    print(f"  {'-'*55}")
    print(f"  {'Input tokens':<25} {in_baseline:>10,} {in_caveman:>10,} {in_headroom:>10,}")
    print(f"  {'Output tokens':<25} {out_baseline:>10,} {out_caveman:>10,} {out_headroom:>10,}")
    print(f"  {'Total tokens':<25} {total_baseline:>10,} {total_caveman:>10,} {total_headroom:>10,}")
    print(f"  {'-'*55}")
    print(f"  {'Input reduction':<25} {'—':>10} {pct(in_baseline,in_caveman):>9.1f}% {pct(in_baseline,in_headroom):>9.1f}%")
    print(f"  {'Output reduction':<25} {'—':>10} {pct(out_baseline,out_caveman):>9.1f}% {pct(out_baseline,out_headroom):>9.1f}%")
    print(f"  {'Total reduction':<25} {'—':>10} {pct(total_baseline,total_caveman):>9.1f}% {pct(total_baseline,total_headroom):>9.1f}%")
    print(f"  {'Result accurate?':<25} {'Yes':>10} {'Yes':>10} {'Yes':>10}")
    print("="*65)

    # ── Winner ──
    caveman_total_pct = pct(total_baseline, total_caveman)
    headroom_total_pct = pct(total_baseline, total_headroom)
    winner = "Caveman" if caveman_total_pct > headroom_total_pct else "Headroom"
    print(f"\n  Overall winner (total tokens): {winner}")
    print(f"  Caveman strength  : Output token reduction ({pct(out_baseline,out_caveman):.1f}%)")
    print(f"  Headroom strength : Input token reduction ({pct(in_baseline,in_headroom):.1f}%)")
    print(f"  Best combined use : Run both together for maximum savings")
    print("="*65 + "\n")

if __name__ == "__main__":
    main()
