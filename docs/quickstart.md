# Get your first signal in 2 minutes

LLMevalIQ gives you deterministic LLM evaluation and production monitoring — no LLM judge, no API cost per eval, no variance.

---

## Option A: Direct Python (no OTel, no infra)

```bash
pip install llmevaliq
```

```python
from llmevaliq.core.test_case import LLMTestCase
from llmevaliq.core.evaluate import evaluate
from llmevaliq.metrics.semantic_similarity import SemanticSimilarityMetric

tc = LLMTestCase(
    input="What is the capital of France?",
    actual_output="Paris is the capital of France.",
    expected_output="Paris",
)
result = evaluate([tc], [SemanticSimilarityMetric()])
# Deterministic. Same score every run. $0.00.
```

---

## Option B: OTel-instrumented app (zero code changes)

```bash
pip install "llmevaliq[otel]"

# Create a baseline from your prompt (once)
llmevaliq baseline collect --name my_baseline --prompt "Answer questions about geography" --n 30

# Start the OTel receiver + monitoring
llmevaliq collect-otel --baseline my_baseline
```

Then point your app's OTel exporter to `localhost:4317` (gRPC) or `localhost:4318` (HTTP).

Compatible with any OTel-instrumented library: `opentelemetry-instrumentation-openai`,
`opentelemetry-instrumentation-anthropic`, LangChain, LlamaIndex, etc.

---

## Option C: File-based monitoring (JSONL)

```bash
# Write traces to a JSONL file from your app, then:
llmevaliq monitor run --baseline my_baseline --source file --path traces.jsonl
```

Each line in `traces.jsonl`:
```json
{"input": "user question", "output": "model response"}
```

---

## See your results in the dashboard

```bash
pip install "llmevaliq[dashboard]"
llmevaliq dashboard
# Opens http://localhost:8501 — interactive drift timeline, attribution, alert log
```

---

## Run the determinism benchmark

```bash
pip install "llmevaliq[benchmark]"
llmevaliq benchmark --tool llmevaliq --runs 5
# LLMevalIQ: std=0.0000, cost=$0.00

# Compare with Groq-backed LLM judge (requires GROQ_API_KEY):
llmevaliq benchmark --tool llmevaliq,groq --runs 5
```

---

## What you get

| Feature | LLMevalIQ | LLM-as-judge (deepeval, ragas) |
|---|---|---|
| Score variance across runs | **0.0000** | 0.3-2.1 |
| Cost per 100 evals | **$0.00** | $0.10-$2.00 |
| Latency per eval | **< 1ms** | 1-5 seconds |
| Requires API key | **No** | Yes |
| Production monitoring | **Yes** | No |
| OTel integration | **Yes** | No |

---

## Next steps

- [OTel integration guide](otel-integration.md) — connect any OTel-instrumented app
- [Dashboard guide](dashboard.md) — navigate the Streamlit dashboard
- [V4 architecture](plans/v4.md) — the full design
