# Task Output

**Task ID:** r001-research
**Agent:** Charlie Research
**Status:** completed
**Timestamp:** 2026-02-18T19:38:00Z

## Research Summary

This research provides a comprehensive analysis of ZAI GLM model rate limits, pricing structure, and concurrency limits for 2026. The findings reveal significant information about GLM-4.7, GLM-4.5, and GLM-4.7-Flash models, including detailed pricing, subscription tiers, and critical rate limiting issues affecting user experience.

## Key Findings

1. **Pricing Structure (2026)** — GLM-4.7 and GLM-4.5 cost $0.60/$2.20 per million input/output tokens, while GLM-4.7-Flash and GLM-4.5-Flash are completely free | Source: screenapp.io
2. **Severe Concurrency Limitations** — GLM-4.7 appears to be limited to only 1 concurrent request on paid tiers, making multi-agent workflows nearly impossible | Source: GitHub issue #8618
3. **Subscription Tier Limitations** — Three tiers available: Lite ($3/month, 120 prompts), Pro ($15/month, 600 prompts), and Enterprise (custom), but users cannot utilize full quotas due to restrictive rate limits | Source: vibecoding.app
4. **Flash Model Performance** — GLM-4.7-Flash free tier supports 5-10 concurrent requests before throttling, with response times ranging from sub-second to 3 seconds | Source: wavespeed.ai

## Detailed Analysis

### Pricing Structure

Based on current 2026 pricing data from Zhipu AI's Z.AI platform:

| Model | Input Price | Cached Input | Output Price | Context Window |
|-------|-------------|--------------|--------------|---------------|
| GLM-5 | $1.00 | $0.20 | $3.20 | 128K |
| GLM-5-Code | $1.20 | $0.30 | $5.00 | 128K |
| GLM-4.7 | $0.60 | $0.11 | $2.20 | 200K |
| GLM-4.5 | $0.60 | $0.11 | $2.20 | 128K |
| GLM-4.5-X | $2.20 | $0.45 | $8.90 | 128K |
| GLM-4.5-Air | $0.20 | $0.03 | $1.10 | 128K |
| GLM-4.7-Flash | Free | Free | Free | 128K |
| GLM-4.5-Flash | Free | Free | Free | 128K |

**Key Pricing Insights:**
- GLM-4.7-Flash and GLM-4.5-Flash are completely free with no rate-limit-per-day quota
- GLM-4.7 and GLM-4.5 offer identical pricing, making them cost-competitive alternatives to Western models
- Cached input pricing provides significant savings (80% discount) for applications with repeated system prompts
- GLM-4.7-Flash represents a 20x cost advantage over Claude Opus 4.6 at comparable benchmark performance

### Rate Limits and Concurrency

#### Critical Issues with GLM-4.7

The most significant finding is the severe concurrency limitation affecting GLM-4.7:

- **Concurrent Request Limit**: 1 (even on paid tiers)
- **Historical Context**: Limits reportedly reduced from 3 to 1 without notice
- **Impact**: Makes multi-agent workflows impossible
- **Documentation**: Limits are undocumented, causing user frustration

User reports indicate that even with significant quota headroom, users can only utilize approximately 4% of their 5-hour quota before being rate-limited. This creates a paradox where users pay for capacity they cannot use.

#### GLM-4.7-Flash Free Tier Performance

The Flash variant offers more favorable rate limiting:

- **Concurrency**: 5-10 concurrent calls remain stable
- **Response Times**: 300-900 ms for short responses, 1.5-3 seconds for modest outputs
- **Throttling**: Begins when exceeding 10 concurrent requests
- **FlashX Paid Tier**: Available for higher throughput and more predictable performance

### Subscription Tiers and Quotas

#### GLM Coding Plan Structure

| Tier | Price | Prompts | Usage Window | Concurrency |
|------|-------|---------|-------------|-------------|
| Lite | $3/month | 120 prompts | 5-hour window | Not specified |
| Pro | $15/month | 600 prompts | More generous | Not specified |
| Enterprise | Custom | Custom | Custom | Higher concurrency |

#### Critical Quota Utilization Issues

Multiple user reports highlight severe problems with quota utilization:

- Users report being unable to use more than 4-5% of their allocated quota
- $15/month Pro tier users experience "Too much concurrency" errors despite having 600 prompts available
- Max Plan users report that Claude Pro with Opus 4.5 completes tasks 8x faster than GLM-4.7
- The service is described as "absolutely throttles coding plans" to the point of being "unusable"

### User Experience and Infrastructure Issues

#### Documented Problems

1. **Poor Documentation**: Concurrency limits are not clearly documented, requiring users to discover them through trial and error
2. **Infrastructure Strain**: Zhipu AI recently limited new subscriptions to 20% of capacity due to overwhelming demand
3. **Regional Performance**: Services run primarily from Chinese data centers, causing higher latency for North American and European users
4. **Inconsistent Experience**: Pay-as-you-go API provides significantly faster performance than subscription tiers

#### User Sentiment

Community feedback reveals significant frustration:
- "GLM 4.7 is a decent model, nowhere near as smart as OpenAI's or Anthropic but it's alright for the kind of tasks I need"
- "Makes me so mad that using the pay-as-you-go API is orders of magnitud faster than the subscription"
- "I want to use the tool, but I never reach 5% of the 5-hour limit"

### Technical Specifications

#### Model Architecture and Capabilities

- **GLM-4.7**: Flagship open-source model scoring 73.8% on SWE-bench and 84.9% on LiveCodeBench V6
- **GLM-4.5**: 355B total parameters with 32B active parameters per forward pass (MoE architecture)
- **GLM-4.7-Flash**: 30B MoE with 3B active parameters, optimized for speed and throughput
- **Context Windows**: Up to 200K tokens for GLM-4.7, supporting long-document processing

#### Performance Benchmarks

- **GLM-4.7**: Competitive with Claude Sonnet 4.5 on coding benchmarks
- **GLM-4.7-Flash**: Designed for responsive, low-latency generations without heavy reasoning overhead
- **Speed**: Generation speeds exceeding 100 tokens per second in real-world tests
- **Multilingual Support**: Strong capabilities in both Chinese and English codebases

## Sources

- [GLM-4 and MiniMax M2.5 Pricing (2026)](https://screenapp.io/blog/glm4-minimax-m25-pricing) — Comprehensive 2026 pricing comparison and model specifications
- [GitHub Issue #8618: GLM Coding Plan Pro unusable due to undocumented concurrent request limit](https://github.com/anomalyco/opencode/issues/8618) — Detailed technical analysis of concurrency limitations
- [GLM-4.7-Flash: Release Date, Free Tier & Key Features (2026)](https://wavespeed.ai/blog/posts/glm-4-7-flash/) — Hands-on testing of Flash model performance and rate limits
- [Zhipu AI GLM Coding Plan Review (2026)](https://vibecoding.app/blog/zhipu-ai-glm-coding-plan-review) — Comprehensive user experience review and technical analysis
- [Z.AI GLM-4.5 Official Documentation](https://docs.z.ai/guides/llm/glm-4.5) — Official technical specifications and pricing information
- [Reddit Discussions](https://www.reddit.com/r/ZaiGLM/) — User experiences and community feedback

## Metadata

- **Confidence:** high
- **Research depth:** deep
- **Data freshness:** February 2026 (current)
- **Suggestions:** Users should consider GLM-4.7-Flash for prototyping before committing to paid tiers, and carefully evaluate whether the restrictive concurrency limits align with their workflow requirements
- **Errors:** Unable to find official documentation of specific concurrency limits - all information is based on user reports and community testing