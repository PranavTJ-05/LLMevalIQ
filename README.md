# LLMevalIQ

[![CI](https://github.com/furyfist/llmevaliq/actions/workflows/ci.yml/badge.svg)](https://github.com/furyfist/llmevaliq/actions)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**Deterministic LLM evaluation and production monitoring. $0/trace. No LLM judge.**

1,000 test cases × 3 metrics → **$0.00** and **4 seconds** instead of **$34.20** and **9,000 API calls**.

---

## Get your first signal in 2 minutes

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

Or with OTel (zero code changes to your app):

```bash
pip install "llmevaliq[otel]"
llmevaliq collect-otel --baseline my_baseline
# point your OTel exporter to localhost:4317
```

Then see your data:

```bash
pip install "llmevaliq[dashboard]"
llmevaliq dashboard
# opens http://localhost:8501
```

---

## The benchmark table

*Accuracy at catching bad outputs on a labeled 100-row QA set (positive class =
bad; thresholds calibrated on a held-out fold). Live run, 2026-07-10.*

| Tool | Precision | Recall | F1 | ROC-AUC | Cost / trace | Deterministic |
|------|-----------|--------|----|---------|--------------|---------------|
| Groq LLM judge | 1.000 | 1.000 | **1.000** | 1.000 | paid | usually, at temp 0 |
| deepeval (G-Eval) | 1.000 | 0.833 | **0.909** | 0.971 | paid | usually, at temp 0 |
| **LLMevalIQ** | 0.806 | 0.967 | **0.879** | 0.857 | **$0.00** | ✅ by construction |
| langfuse-style | 0.612 | 1.000 | **0.760** | 0.525 | paid | usually, at temp 0 |

**The honest read:** on subtle, lexically-close wrong answers, a real LLM judge
beats LLMevalIQ's embedding metric on accuracy — and we say so. LLMevalIQ's edge is
being **deterministic and $0/trace by construction**, and staying useful where
judges default to passing everything (on the summarization / RAG sets the judges
collapse to F1 0.667 while LLMevalIQ scores 1.0). They are complementary. Full
tables, the fairness rule, and a per-item audit trail:
[`BENCHMARK_ACCURACY.md`](BENCHMARK_ACCURACY.md).

> Run this yourself: `llmevaliq benchmark --tool llmevaliq --runs 5 --metric accuracy`
> Full suite (Groq key): `llmevaliq benchmark --tool llmevaliq,groq,deepeval,ragas,langfuse --runs 5 --metric accuracy`

---

## Architecture

```
                 ┌─────────────────────────────────────┐
                 │         Streamlit Dashboard          │  ← V4
                 │  reads SQLite, renders interactive   │
                 └──────────────┬──────────────────────┘
                                │ reads
     ┌──────────────────────────┼──────────────────────┐
     │                   SQLite DB                      │
     │  baselines │ timeline │ alerts │ components      │
     └──────────────────────────┬──────────────────────┘
                                │ writes
┌───────────────────────────────┼───────────────────────┐
│              V1-V3 Pipeline (untouched)                │
│  Metrics → Monitor → TimelineStore → Attribution      │
└───────────────────────────────┬───────────────────────┘
                                │ feeds
┌───────────┬───────────┬───────┴───┬───────────────────┐
│  File     │ Langfuse  │   SDK     │  OTelCollector    │  ← V4
│ Collector │ Collector │ Collector │  OTLP/gRPC+HTTP   │
└───────────┴───────────┴───────────┴───────────────────┘
```

V4 adds one collector at the bottom and one visualization layer at the top. The middle is untouched.

---

## Features

### V1 — Deterministic evaluation
- `SemanticSimilarityMetric` — cosine similarity with sentence-transformers
- `OutputStabilityMetric` — distributional consistency against a reference sample
- `ConsistencyMetric` — self-consistency across paraphrased prompts
- `ResponseDriftMetric` — statistical drift detection (PSI, KS, JS divergence)

### V2 — Production monitoring
- `Monitor` — stream traces from file, Langfuse, or SDK; score against baseline
- `TimelineStore` — SQLite-backed score time series with trend analysis
- `AlertEngine` — consecutive-failure alerts with JSONL + SQLite logging
- Collectors: `FileCollector`, `LangfuseCollector`, `SDKCollector`

### V3 — Root-cause attribution
- PELT changepoint detection per component
- CUSUM online alarms
- Cascade attribution: identifies root-cause component and downstream cascades
- `llmevaliq attribute` CLI command with terminal report and PNG export

### V4 — Ecosystem entry (this release)
- **OTelCollector** — OTLP/gRPC + HTTP receiver; auto-maps GenAI semconv spans
- **Streamlit dashboard** — 4 pages: Overview, Drift Timeline, Attribution, Alert Log
- **Accuracy benchmark** — compare LLMevalIQ vs Groq/deepeval/ragas/langfuse on precision/recall/F1 at catching bad outputs (plus cost and determinism)
- **Quickstart overhaul** — 2-line first-signal experience
- **Generic span support** — `llmevaliq.*` attributes for non-GenAI apps

---

## Install

```bash
# Core eval + monitoring
pip install llmevaliq

# OTel receiver
pip install "llmevaliq[otel]"

# Local dashboard
pip install "llmevaliq[dashboard]"

# Benchmark suite
pip install "llmevaliq[benchmark]"

# Groq baseline collection
pip install "llmevaliq[groq]"

# Everything
pip install "llmevaliq[all]"
```

---

## CLI reference

```bash
# Baseline management
llmevaliq baseline collect --name my_baseline --prompt "..." --source groq --n 30
llmevaliq baseline list
llmevaliq baseline show my_baseline

# Production monitoring
llmevaliq monitor run --baseline my_baseline --source file --path traces.jsonl
llmevaliq collect-otel --baseline my_baseline   # NEW: OTel receiver

# Timeline inspection
llmevaliq timeline show --metric ResponseDriftMetric
llmevaliq timeline summary --metric SemanticSimilarityMetric
llmevaliq timeline export --metric ResponseDriftMetric --output chart.png

# Pipeline attribution (V3)
llmevaliq pipeline run --name my_pipeline --path traces.jsonl
llmevaliq attribute --pipeline my_pipeline --last 500

# Dashboard (V4)
llmevaliq dashboard                             # NEW
llmevaliq dashboard --db llmevaliq.db --port 8501

# Benchmark (V4)
llmevaliq benchmark --tool llmevaliq --runs 5 --metric accuracy      # NEW
llmevaliq benchmark --tool llmevaliq,groq,deepeval,ragas,langfuse --runs 3 --metric accuracy
```

---

## Comparison

| Feature | LLMevalIQ | deepeval | ragas | Phoenix | Langfuse |
|---|---|---|---|---|---|
| Deterministic by construction (no LLM call) | ✅ | ❌ | ❌ | ❌ | ❌ |
| $0 per eval | ✅ | ❌ | ❌ | ❌ | ❌ |
| Production monitoring | ✅ | ❌ | ❌ | ✅ | ✅ |
| Changepoint attribution | ✅ | ❌ | ❌ | ❌ | ❌ |
| OTel integration | ✅ | ❌ | ❌ | ✅ | ✅ |
| Local dashboard | ✅ | ❌ | ❌ | ✅ | ✅ |
| No cloud required | ✅ | ✅ | ✅ | ❌ | ❌ |
| No API key to evaluate | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## Documentation

- [Quickstart](docs/quickstart.md) — 2-minute first signal
- [OTel integration](docs/otel-integration.md) — connect any OTel app
- [Dashboard guide](docs/dashboard.md) — navigate the Streamlit UI
- [V4 build plan](docs/plans/v4.md) — architecture and design decisions

---

## License

Apache 2.0
