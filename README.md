 REQUIRMENTS:
pandas==2.1.4
numpy==1.24.3
plotly==5.17.0
yfinance==0.2.28
scipy==1.11.4
pyyaml==6.0.1

# 🔥 Liquidity Sweep Heatmap - ICT Trading Tool

**Detects ICT liquidity sweeps with heatmap visualization!**

## 🚀 Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt






     Features
    ✅ ICT Swing High/Low sweeps
   ✅ Liquidity heatmap overlay
  ✅ Confidence scoring
 ✅ Interactive Plotly charts
 ✅ Backtest statistics
 ✅ Multiple timeframe support






A model that predicts $189.30 when actual is $191.20 has a $1.90 error. But if both the prediction and reality went UP from $188.00, the model got the direction right — the thing that matters for trading. MAPE of 1% with 57% directional accuracy is a more complete picture than RMSE alone.





ict judas swing is more inportant



# ⚡ ICT Judas Swing Detector

Automatically detects **ICT Judas Swing** patterns on Forex 15M data across London and New York sessions — one of the most powerful manipulation concepts in Inner Circle Trader (ICT) methodology.

![Judas Swing Output](output.png)

---

## 🧠 What is a Judas Swing?

ICT teaches that **Smart Money deceives retail traders** at session opens by making a fake move in the wrong direction first — raiding liquidity above/below the previous session's range — then reversing violently in the **true direction** for that session.

```
London Open Judas (raids Asia Range):
  ┌─────────────────────────────────────┐
  │  Asia High ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │  ← price spikes ABOVE (bearish judas)
  │  [Asia consolidation range]         │
  │  Asia Low  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │  ← price spikes BELOW (bullish judas)
  └─────────────────────────────────────┘
       ↑ London Open: Judas raids one side → reverses → real move begins
```

**NY Open Judas** works the same way but raids the **London session range**.

---

## ✅ Features

- Detects **Bullish** and **Bearish** Judas Swings at both London & NY opens
- Builds **Asia Range** and **London Range** automatically from session hours
- Filters small spikes with configurable minimum pip threshold
- Color-coded session background (Asia / London / NY / Close)
- Annotated chart with raid size in pips + trade bias (LONG / SHORT)
- Console summary with full event log

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install pandas numpy matplotlib
```

### 2. Run
```bash
python judas_swing.py
```

Chart saved as `output.png`. Console prints all detected events with pip raid sizes.

---

## ⚙️ Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `LONDON_OPEN_HOUR` | 8 UTC | London session open hour |
| `NY_OPEN_HOUR` | 13 UTC | NY session open hour |
| `MIN_RAID_PIPS` | 3 | Minimum pips beyond range to qualify |
| `RAID_REVERSAL_CANDLES` | 4 | Max candles allowed before reversal |

---

## 📊 Sample Output (5 days, EUR/USD 15M)

```
Total Judas Swings detected : 11
Bullish (Long Bias)         : 6
Bearish (Short Bias)        : 5
London Session              : 5
NY Session                  : 6
Avg Raid Size               : 13.1 pips
Max Raid Size               : 29.2 pips
```

---

## 🔌 Use with Real Data

Replace the data generator with your broker feed or yfinance:

```python
import yfinance as yf
df = yf.download("EURUSD=X", period="10d", interval="15m")
df.columns = [c.lower() for c in df.columns]
```

---

## 📁 Project Structure

```
ict-judas-swing-detector/
├── judas_swing.py    # Main detector script
├── output.png        # Sample chart output
└── README.md
```

---

## 📚 ICT Concepts Used

| Concept | Role in Script |
|---|---|
| Asia Range | Reference range for London Judas raids |
| London Range | Reference range for NY Judas raids |
| Liquidity Raid | Wick beyond range → triggers detection |
| Judas Swing | Fake direction → reversal = true bias |
| Session Killzones | London 08:00–10:00 UTC, NY 13:00–15:00 UTC |

---

## 🛠 Requirements

- Python 3.8+
- pandas · numpy · matplotlib

---

## 📄 License

MIT License


