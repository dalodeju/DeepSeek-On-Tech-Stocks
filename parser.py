import pandas as pd
from datetime import datetime
import argparse
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_args():
    parser = argparse.ArgumentParser(description='Parse news headlines for sentiment analysis.')
    parser.add_argument('--query', type=str, default='NVDA OR "tech news" site:finance.yahoo.com OR site:bloomberg.com after:2025-01-25 before:2025-01-29', help='Google News search query')
    parser.add_argument('--output', type=str, default='tech_news_sentiment.xlsx', help='Output Excel file')
    parser.add_argument('--delay', type=float, default=3.0, help='Delay between scrolls (seconds)')
    parser.add_argument('--scrolls', type=int, default=5, help='Number of times to scroll for more results')
    return parser.parse_args()

sentiment_keywords = {
    'alarm': [
        'warning', 'drop', 'crash', 'concern', 'risk', 'loss', 'decline', 'bear', 'fear', 'sell-off', 'plunge', 'volatile', 'lawsuit', 'investigation', 'fraud', 'scandal', 'downturn', 'recession', 'layoff', 'cut', 'regulation', 'ban', 'fine', 'penalty', 'recall', 'hack', 'breach', 'scare', 'shortfall', 'miss', 'disappoint', 'collapse', 'bubble', 'panic', 'fire', 'explosion', 'shutdown', 'delay', 'deficit', 'lawsuit', 'probe', 'scam', 'controversy', 'lawsuit', 'lawsuit', 'lawsuit'
    ],
    'opportunity': [
        'gain', 'buy', 'strong', 'growth', 'opportunity', 'bull', 'rally', 'surge', 'record', 'profit', 'beat', 'outperform', 'expansion', 'innovation', 'launch', 'acquire', 'merger', 'deal', 'partnership', 'investment', 'funding', 'award', 'win', 'approval', 'breakthrough', 'milestone', 'success', 'upgrade', 'positive', 'recovery', 'rebound', 'hire', 'expansion', 'open', 'increase', 'rise', 'improve', 'boost', 'lead', 'advance', 'soar', 'skyrocket', 'all-time high', 'top', 'best', 'strongest', 'record-breaking'
    ],
}

def classify_sentiment(title):
    title_lower = title.lower()
    for tag, keywords in sentiment_keywords.items():
        if any(kw in title_lower for kw in keywords):
            return tag
    return 'neutral'

def main():
    args = parse_args()
    logging.info(f"Searching Google News for: {args.query}")
   
    chrome_options = Options()

    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    search_url = f'https://news.google.com/search?q={quote_plus(args.query)}&hl=en-US&gl=US&ceid=US:en' 
    driver.get(search_url)
    time.sleep(args.delay)

    try:
        reject_button = driver.find_element(By.XPATH, "//button[contains(., 'Reject all') or contains(., 'Reject cookies') or contains(., 'I disagree')] | //div[@role='button'][contains(., 'Reject all') or contains(., 'Reject cookies')] ") # Attempt to find reject button by text or role
        reject_button.click()
        logging.info("Clicked 'Reject cookies' or similar button.")
        time.sleep(args.delay) 
    except Exception as e:
        logging.info(f"No cookie consent pop-up or reject button found/clicked: {e}")

    for _ in range(args.scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(args.delay)
   
    with open("google_news_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
   
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    articles = []
   
    for article_container in soup.select('article.IFHyqb'): # Use a more specific article selector
       
        headline_link_tag = article_container.select_one('a.JtKRv')
        title = headline_link_tag.get_text() if headline_link_tag else 'No Headline Found'
        url = headline_link_tag.get('href') if headline_link_tag else 'No URL Found'

      
        if url and url.startswith('./read/'):
            url = f'https://news.google.com{url[1:]}' 

        date_tag = article_container.select_one('time.hvbAAd')
        date_text = 'No Date Found'
        if date_tag:

            raw_date_str = date_tag.get('datetime')
            if raw_date_str:
                try:
                    
                    date_obj = datetime.fromisoformat(raw_date_str.replace('Z', '+00:00')) 
                    date_text = date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    logging.warning(f"Could not parse date from datetime attribute: {raw_date_str}")
                    date_text = date_tag.get_text(strip=True) 
            else:
                
                date_text = date_tag.get_text(strip=True)


        articles.append({
            'Date': date_text,
            'Headline': title,
            'Source': url, 
            'Sentiment': classify_sentiment(title),
        })

    if not articles:
        logging.warning("No articles found for the given parameters.")
    df = pd.DataFrame(articles)
    df.to_excel(args.output, index=False)
    logging.info(f"Saved {len(df)} headlines to {args.output}")

if __name__ == '__main__':
    main()
