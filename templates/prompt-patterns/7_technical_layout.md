# Template 7: Technical Layout & Trading Strategy

**Category:** Technical Analysis
**Role:** Senior Quantitative Trader
**Language:** English
**Usage:** Complete technical analysis report for trading strategy

---

## Prompt Template

```
You are a senior quantitative trading expert capable of combining technical indicators with statistical models to optimize trade timing. Prepare a complete technical analysis report, including:

• Trend assessment covering daily, weekly, and monthly timeframes
• Key support and resistance levels with precise price points
• [STRATEGY NAME] signal analysis with [STRATEGY PARAMS]
• [POSITION MANAGEMENT] evaluation
• [RISK MANAGEMENT] criteria
• Risk-reward ratio calculations
• Trading confidence rating: Strong Buy, Buy, Neutral, Sell, Strong Sell

Please organize the results as a technical analysis scorecard with a concise trading plan summary.

Strategy to analyze:
[INSERT YOUR STRATEGY DETAILS]
```

---

## Key Output Fields

- **Trend Assessment:** Daily / Weekly / Monthly
- **Support/Resistance:** Precise price levels
- **Signal Analysis:** Strategy-specific indicators
- **Position Management:** Entry/exit rules
- **Risk Management:** Stop loss, position sizing
- **Risk-Reward Ratio:** Calculated values
- **Confidence Rating:** 5-point scale

---

## Example Usage (TW Supertrend Strategy)

```
You are a senior quantitative trading expert capable of combining technical indicators with statistical models to optimize trade timing. Prepare a complete technical analysis report, including:

• Trend assessment covering daily, weekly, and monthly timeframes
• Key support and resistance levels with precise price points
• Supertrend signal analysis (length=10, multiplier=3.0)
• Phased entry evaluation (days 1/4/7, 33% each)
• Dynamic risk management (day 7/11 assessment)
• False breakout detection (day 7 loss > 3%)
• Risk-reward ratio calculations
• Trading confidence rating: Strong Buy, Buy, Neutral, Sell, Strong Sell

Please organize the results as a technical analysis scorecard with a concise trading plan summary.

Strategy to analyze:
TW Supertrend Strategy - Phased Entry with Dynamic Risk Management
- Asset Pool: 100+ stocks across 11 sectors
- Entry Phases: Day 1/4/7, 33% each
- Risk Management: Day 7/11 evaluation, stop loss if loss > 3% on day 7
- Parameters: Supertrend length=10, multiplier=3.0
```

---

## Common Strategy Parameters

**Supertrend Strategy:**
- length: 10 (default), can be 7-15
- multiplier: 3.0 (default), can be 2-5
- Timeframe: Daily (recommended)

**MACD Strategy:**
- fast_period: 12
- slow_period: 26
- signal_period: 9
- Timeframe: Daily or 4H

**RSI Strategy:**
- period: 14
- overbought: 70
- oversold: 30
- Timeframe: Daily or 4H

**Bollinger Bands Strategy:**
- period: 20
- std_dev: 2
- Timeframe: Daily

---

## Output Format Example

```
# Technical Analysis Scorecard

## Trend Assessment
| Timeframe | Trend | Strength | Key Levels |
|-----------|-------|----------|-------------|
| Daily | Uptrend | Strong | Support: $150, Resistance: $165 |
| Weekly | Sideways | Moderate | Support: $145, Resistance: $170 |
| Monthly | Uptrend | Strong | Support: $130, Resistance: $180 |

## Signal Analysis
- Supertrend (10, 3.0): BUY signal confirmed
- Signal Strength: 8/10
- Confirmation Volume: Above average

## Risk Management
- Stop Loss: $148 (3.2% below current)
- Risk-Reward Ratio: 1:3.2
- Position Size: 5% of portfolio

## Trading Plan
**Confidence Rating:** STRONG BUY (8.5/10)

**Entry Strategy:**
- Phase 1 (Day 1): 33% at market open
- Phase 2 (Day 4): 33% if price > $155
- Phase 3 (Day 7): 34% if price > $160

**Exit Strategy:**
- Take Profit: $168 (target 12% gain)
- Stop Loss: $148 (limit 3.2% loss)
- Re-evaluation: Day 7 and Day 11
```

---

## Tips for Best Results

1. **Specify Timeframes:**
   - Daily for swing trading
   - 4H for intraday
   - Weekly for long-term

2. **Define Risk Tolerance:**
   - Conservative: 1-2% stop loss
   - Moderate: 3-5% stop loss
   - Aggressive: 5-10% stop loss

3. **Include Position Sizing:**
   - Helps with portfolio risk management
   - Affects confidence rating

4. **Mention Asset Class:**
   - Stocks: Different volatility characteristics
   - Crypto: Higher volatility, wider stops
   - Forex: 24/7 market, different session behavior

---

## Confidence Rating Criteria

| Rating | Description | Typical Action |
|--------|-------------|----------------|
| Strong Buy | 8-10/10 | Maximum position, tight stop |
| Buy | 6-8/10 | Full position, normal stop |
| Neutral | 4-6/10 | Small position, wide stop |
| Sell | 2-4/10 | Reduce or exit position |
| Strong Sell | 0-2/10 | Exit all positions immediately |

---

**Last Updated:** 2026-03-12
**Version:** v1.0
**Created By:** v4.0 Charlie
**Application:** Web 4.0 Economic Plan - TW Supertrend Strategy
