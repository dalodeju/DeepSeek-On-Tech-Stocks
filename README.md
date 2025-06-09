# The Release of DeepSeek R1 on Tech Stocks 

A cross-tool analysis of how the Jan 27 2025 release of DeepSeek’s R1 AI model shook—and then spurred a rebound in—major tech stocks. This repo combines:

- **Sentiment analysis** on news headlines (alarm / opportunity / neutral)
- **OHLCV stock-price dashboards** in Power BI
- **A guided report** tying sentiment swings to price moves

---

## 1. Headline Parser

A Python script that scrapes Google News headlines for a custom query window (default Jan 25–29, 2025), classifies each headline’s sentiment, and exports to Excel.

### Features
- **Selenium + BeautifulSoup** to scroll & parse Google News  
- Configurable search query, scroll depth, and delay  
- Keyword-based sentiment tagging (`alarm`, `opportunity`, `neutral`)  
- Save raw HTML snapshot (`google_news_page.html`) and final Excel  

### Requirements
- Python 3.8+  
- Google Chrome  
- A ChromeDriver managed via `webdriver-manager`  

Install dependencies:

```bash
cd parser
pip install -r requirements.txt
```

### Usage
```bash
python parser.py \
  --query "NVDA OR tech news site:finance.yahoo.com OR site:bloomberg.com after:2025-01-25 before:2025-01-29" \
  --output "../data/tech_news_sentiment.xlsx" \
  --delay 3 \
  --scrolls 5
```

| Argument    | Description                                   | Default                                                                                             |
| ----------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `--query`   | Google News search query                      | `NVDA OR tech news site:finance.yahoo.com OR site:bloomberg.com after:2025-01-25 before:2025-01-29` |
| `--output`  | Path to output Excel file                     | `data/tech_news_sentiment.xlsx`                                                                     |
| `--delay`   | Delay (seconds) between scrolls               | `3`                                                                                                 |
| `--scrolls` | Number of scroll actions to load more results | `5`                                                                                                 |

## 2. Price Data CSVs

Six CSV files in `data/`—one per ticker/index—cover daily OHLCV from **Oct 1 2024** through **Mar 31 2025** from Yahoo Finance:

- **Alphabet A (GOOGL) Historical Data OCT24-MAR25.csv**  
- **Broadcom (AVGO) Historical Data OCT24-MAR25.csv**  
- **Microsoft (MSFT) Historical Data OCT24-MAR25.csv**  
- **Nasdaq 100 Historical Results Price Data OCT24-MAR25.csv**  
- **NVIDIA (NVDA) Historical Data OCT24-MAR25.csv**  
- **QQQ Historical Data OCT24-MAR25.csv**  

Each CSV has columns:

```
Date, Open, High, Low, Close, Volume
```

---

## 3. Power BI Report

The file `reports/The Release of DeepSeek on Tech Giants.pbix` contains:

- **Data mashup**  
  Combined all six CSVs plus `tech_news_sentiment.xlsx` via Power Query  
- **Relationship model**  
  Date joins between the merged price table and event-metadata table  
- **DAX measures**  
  - Daily % change  
  - Sentiment-score summaries  
  - “Days from event” calculation  
- **What-If parameter**  
  Adjustable event window (±3, ±7, ±14 days)  
- **Visuals**  
  - **Bar chart**: Sentiment Score by date (Jan 25–29)  
  - **Line charts**: Price indexed to Day 0 (Jan 26) for each ticker  
- **Interactivity**  
  Dynamic titles, tooltips, slicers, and parameter controls for exploration  
