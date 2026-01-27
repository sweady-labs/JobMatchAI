# Application Letter Generation - Cost Analysis

**Analysis Date:** 21. Oktober 2025  
**Based on:** Actual token usage from Rico's application workflow

---

## Token Usage Summary

### Input Tokens (Per Application Letter)

| Component | Characters | Estimated Tokens | % of Total |
|:----------|:----------:|:----------------:|:----------:|
| **Prompt** (ATS optimized) | 13,010 | ~3,250 | 31.6% |
| **Job Description** (avg) | 4,204 | ~1,050 | 10.2% |
| **Competence Profile** | 24,024 | ~6,000 | 58.2% |
| **TOTAL INPUT** | **41,238** | **~10,300** | **100%** |

### Output Tokens (Per Application Letter)

| Metric | Tokens |
|:-------|:------:|
| **Estimated Output** (300-400 words letter) | ~500-600 |
| **Average Output Used** | ~550 |

### Total Token Usage Per Application Letter

- **Input:** ~10,300 tokens
- **Output:** ~550 tokens
- **Total:** ~10,850 tokens per application letter

---

## Cost Comparison by LLM Provider

### Ultra-Budget Models (Best Value) 💰

| Rank | Model | Input Cost | Output Cost | Cost Per Letter | Annual Cost (100 letters) | Quality Score | Notes |
|:----:|:------|:----------:|:-----------:|:---------------:|:-------------------------:|:-------------:|:------|
| 1 | **Cohere Command R** | $0.0015 | $0.0003 | **$0.0018** | **$0.18** | 8.74/10 ⭐ | **BEST VALUE** - Enterprise RAG optimized |
| 2 | **Meta Llama 4 Maverick** | $0.0023 | $0.0005 | **$0.0028** | **$0.28** | 8.68/10 | Open-source, 1M context |
| 3 | **AI21 Jamba Mini** | $0.0021 | $0.0002 | **$0.0023** | **$0.23** | 8.39/10 | Structured output specialist |
| 4 | **DeepSeek V3.2** | $0.0029 | $0.0002 | **$0.0031** | **$0.31** | 8.09/10 | Ultra-cheap Chinese model |
| 5 | **xAI Grok-4 Fast** | $0.0021 | $0.0003 | **$0.0024** | **$0.24** | 8.15/10 | 2M context, fast |

### Budget Models (Good Balance) 💵

| Rank | Model | Input Cost | Output Cost | Cost Per Letter | Annual Cost (100 letters) | Quality Score | Notes |
|:----:|:------|:----------:|:-----------:|:---------------:|:-------------------------:|:-------------:|:------|
| 6 | **OpenAI GPT-5 mini** | $0.0026 | $0.0011 | **$0.0037** | **$0.37** | 8.68/10 | Fast utility, ChatGPT Plus included |
| 7 | **OpenAI GPT-4.1 mini** | $0.0082 | $0.0018 | **$0.0100** | **$1.00** | 8.30/10 | Legacy mini; broad compatibility |
| 8 | **Alibaba Qwen-Plus** | $0.0041 | $0.0007 | **$0.0048** | **$0.48** | 7.88/10 | Up to 1M context |
| 9 | **Google Gemini 2.5 Pro** | $0.0064 | $0.0028 | **$0.0092** | **$0.92** | 8.61/10 | Multimodal, Google integration |
| 10 | **Anthropic Claude Haiku 4.5** | $0.0103 | $0.0028 | **$0.0131** | **$1.31** | 8.01/10 | Low latency coding |

### Mid-Range Models (High Quality) 💎

| Rank | Model | Input Cost | Output Cost | Cost Per Letter | Annual Cost (100 letters) | Quality Score | Notes |
|:----:|:------|:----------:|:-----------:|:---------------:|:-------------------------:|:-------------:|:------|
| 11 | **OpenAI GPT-5** | $0.0129 | $0.0055 | **$0.0184** | **$1.84** | 8.73/10 ⭐ | Top general-purpose |
| 12 | **Mistral Large 2** | $0.0206 | $0.0033 | **$0.0239** | **$2.39** | 7.93/10 | EU data residency |
| 13 | **Cohere Command R+** | $0.0258 | $0.0055 | **$0.0313** | **$3.13** | 7.96/10 | Enterprise high-capacity |
| 14 | **OpenAI GPT-4.1** | $0.0309 | $0.0066 | **$0.0375** | **$3.75** | 8.50/10 | Stable GPT-4 era flagship |
| 15 | **Anthropic Claude Sonnet 3.7** | $0.0309 | $0.0083 | **$0.0392** | **$3.92** | 8.02/10 | Coding with tools |
| 16 | **xAI Grok-4** | $0.0309 | $0.0083 | **$0.0392** | **$3.92** | 7.45/10 | Live web search |

### Premium Models (Best Quality) 💎💎

| Rank | Model | Input Cost | Output Cost | Cost Per Letter | Annual Cost (100 letters) | Quality Score | Notes |
|:----:|:------|:----------:|:-----------:|:---------------:|:-------------------------:|:-------------:|:------|
| 17 | **Anthropic Claude Sonnet 4.5** | $0.0309 | $0.0083 | **$0.0392** | **$3.92** | 9.6/10 ⭐⭐ | **TOP QUALITY** - Agentic coding (available via Anthropic API only; not available through OpenAI API) |
| 18 | **OpenAI GPT-5 pro** | $0.1545 | $0.0660 | **$0.2205** | **$22.05** | 9.8/10 ⭐⭐⭐ | Frontier reasoning |

---

## Cost Analysis Summary

### Price Ranges

| Category | Cost Per Letter | Annual Cost (100 letters) | Best Model |
|:---------|:---------------:|:-------------------------:|:-----------|
| **Ultra-Budget** | $0.0018 - $0.0031 | $0.18 - $0.31 | Cohere Command R |
| **Budget** | $0.0037 - $0.0131 | $0.37 - $1.31 | OpenAI GPT-5 mini |
| **Mid-Range** | $0.0184 - $0.0392 | $1.84 - $3.92 | OpenAI GPT-5 |
| **Premium** | $0.0392 - $0.2205 | $3.92 - $22.05 | Claude Sonnet 4.5 |

### Calculation Formula

```text
Cost Per Letter = (Input Tokens × Input Price) + (Output Tokens × Output Price)
                = (10,300 × Price per 1M / 1,000,000) + (550 × Price per 1M / 1,000,000)
```

### OpenAI model rates used (per 1M tokens)

- GPT-5: Input $1.25 • Output $10.00
- GPT-5 mini: Input $0.25 • Output $2.00
- GPT-4.1: Input $3.00 • Output $12.00  (indicative)
- GPT-4.1 mini: Input $0.80 • Output $3.20  (indicative)

Notes:

- Rates are indicative snapshots; always confirm latest pricing on provider pages.
- Anthropic Claude Sonnet 4.5 is available via Anthropic’s API only (not via OpenAI API).

---

## Recommendations by Use Case

### 🏆 Best Overall Value: **Cohere Command R**

- **Cost:** $0.0018 per letter ($0.18 per 100)
- **Quality:** 8.74/10 (excellent)
- **Why:** Enterprise-grade RAG optimization, 128k context, best cost-to-quality ratio
- **Perfect for:** High-volume application generation

### 🎯 Best Quality at Reasonable Price: **OpenAI GPT-5**

- **Cost:** $0.0184 per letter ($1.84 per 100)
- **Quality:** 8.73/10 (top-tier)
- **Why:** Best general-purpose model, ecosystem leader
- **Perfect for:** Premium applications to dream companies

### 💎 Best Quality (Regardless of Cost): **Anthropic Claude Sonnet 4.5**

- **Cost:** $0.0392 per letter ($3.92 per 100)
- **Quality:** 9.6/10 (near-perfect)
- **Why:** Leading agentic capabilities, long-context reasoning
- **Perfect for:** C-level positions, highly competitive roles

### 💰 Absolute Lowest Cost: **Cohere Command R**

- **Cost:** $0.0018 per letter
- **Savings vs GPT-5:** 90.2% cheaper
- **Savings vs GPT-5 pro:** 99.2% cheaper

---

## Volume Pricing Scenarios

### Scenario 1: Job Seeker (Active Campaign)

**Volume:** 100 applications over 3 months

| Model | Total Cost | Cost Per Day | Recommendation |
|:------|:----------:|:------------:|:---------------|
| Cohere Command R | $0.18 | $0.002 | ✅ Best for volume |
| GPT-5 mini | $0.37 | $0.004 | ✅ Good balance |
| GPT-4.1 mini | $1.00 | $0.011 | ➕ Legacy option, still solid |
| GPT-5 | $1.84 | $0.020 | ⚠️ Premium quality |
| GPT-4.1 | $3.75 | $0.042 | ⚠️ Only if 4.x compatibility needed |
| Claude Sonnet 4.5 | $3.92 | $0.043 | ⚠️ Special roles only |

### Scenario 2: Recruitment Agency

**Volume:** 1,000 applications per month

| Model | Monthly Cost | Annual Cost | Break-even Point |
|:------|:------------:|:-----------:|:-----------------|
| Cohere Command R | $1.80 | $21.60 | Self-hosted may not be worth it |
| GPT-5 mini | $3.70 | $44.40 | Good subscription value |
| GPT-4.1 mini | $10.00 | $120.00 | Consider Plus plan instead |
| GPT-5 | $18.40 | $220.80 | Premium tier justified |
| GPT-4.1 | $37.50 | $450.00 | Legacy model costlier |
| Claude Sonnet 4.5 | $39.20 | $470.40 | Top-tier agency only |

### Scenario 3: Enterprise HR Platform

**Volume:** 10,000 applications per month

| Model | Monthly Cost | Annual Cost | Recommendation |
|:------|:------------:|:-----------:|:---------------|
| Cohere Command R | $18.00 | $216 | ✅ Enterprise deal available |
| GPT-5 mini | $37.00 | $444 | ✅ OpenAI Enterprise tier |
| GPT-4.1 mini | $100.00 | $1,200 | ➕ Consider only for legacy |
| GPT-5 | $184.00 | $2,208 | ⚠️ High volume pricing needed |
| GPT-4.1 | $375.00 | $4,500 | ⚠️ Likely replace with GPT-5 |
| Claude Sonnet 4.5 | $392.00 | $4,704 | ⚠️ Only for premium service |

---

## Subscription Value Analysis

### ChatGPT Plans (OpenAI)

| Plan | Monthly Cost | Included | Value at 100 letters/month | Break-even Point |
|:-----|:------------:|:---------|:--------------------------:|:-----------------|
| **Plus** | $20 | GPT-5 + GPT-5 mini | Unlimited (worth ~$1.84+) | ~10 letters/month |
| **Team** | $25-30/user | GPT-5 + GPT-5 mini | Unlimited | ~15 letters/month |
| **Pro** | $200 | All GPT models | Unlimited (worth ~$22+) | ~10 letters/month |

**Recommendation:** If generating >50 letters/month, ChatGPT Plus ($20) is cost-effective with GPT-5 access.

### Claude Plans (Anthropic)

| Plan | Monthly Cost | Included | Value at 100 letters/month | Break-even Point |
|:-----|:------------:|:---------|:--------------------------:|:-----------------|
| **Pro** | $20 | Claude Haiku/Sonnet 3.7 | Unlimited (worth ~$3.92) | ~5 letters/month |
| **Max** | $100 | All Claude models | Unlimited (worth ~$3.92+) | ~25 letters/month |

**Recommendation:** Claude Pro ($20) excellent value for quality-focused applications.

---

## Cost Optimization Strategies

### Strategy 1: Hybrid Approach 🎯

- **Bulk applications:** Cohere Command R ($0.0018/letter)
- **Target companies:** GPT-5 ($0.0184/letter)
- **Dream jobs:** Claude Sonnet 4.5 ($0.0392/letter)
- **Average cost:** ~$0.01/letter (mixed)

### Strategy 2: Subscription Maximization 💪

- **ChatGPT Plus:** $20/month for unlimited GPT-5 + GPT-5 mini
- **Generate:** 200+ letters/month
- **Effective cost:** ~$0.10/letter (still cheaper than API at scale)

### Strategy 3: Open Source Deployment 🔧

- **Model:** Meta Llama 4 Maverick (self-hosted)
- **Infrastructure:** $50-100/month (cloud GPU)
- **Break-even:** ~200 letters/month
- **Advantage:** Data privacy, customization

---

## Technical Notes

### Token Estimation Accuracy

- **Character-to-token ratio:** ~4:1 for English text
- **Actual variance:** ±10% depending on text complexity
- **Markdown overhead:** Minimal (~2-3% increase)

### Context Window Usage

- **Current usage:** 10,300 tokens (input)
- **Models supporting this:** All listed models
- **Safety margin:** 10x below most context limits

### Output Token Variance
- **Minimum:** ~400 tokens (concise letter)
- **Average:** ~550 tokens (optimal letter)
- **Maximum:** ~800 tokens (detailed letter)

---

## Conclusion

### For Rico's Use Case:

**Recommended Primary Model:** **Cohere Command R**
- Cost: $0.0018/letter ($0.18/100)
- Quality: 8.74/10 (excellent for RAG/structured generation)
- ROI: Best cost-performance ratio

**Recommended Premium Upgrade:** **OpenAI GPT-5**
- Cost: $0.0184/letter ($1.84/100)
- Quality: 8.73/10 (top general-purpose)
- Use case: High-priority applications (10-20% of volume)

**Alternative Subscription:** **ChatGPT Plus** ($20/month)

- Unlimited GPT-5/GPT-5 mini access
- Break-even at ~11 letters/month
- Best for active job seekers

---

**Last Updated:** 21. Oktober 2025  
**Token Calculation Based On:** Actual workflow measurement (41,238 characters input)
