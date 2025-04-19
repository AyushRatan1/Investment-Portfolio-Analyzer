#!/usr/bin/env python3
"""
Multi-Source News Fetcher
Gets stock news and market data from multiple sources
"""

import os
import re
import json
import time
import random
import requests
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Model to store news data consistently across sources
class NewsItem(BaseModel):
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[str] = None
    sentiment: Optional[str] = None

class MultiFetchNewsProvider:
    """
    News provider that fetches from multiple sources and combines results
    """
    
    def __init__(self, api_key=None):
        self.news_api_key = api_key or os.getenv("NEWS_API_KEY")
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
        ]
        
        # Define sources to fetch from - we'll add more as needed
        self.news_sources = [
            self._get_news_api,    # If API key is available
            self._get_yahoo_finance,
            self._get_market_watch,
            self._get_google_finance
        ]
    
    def _get_random_user_agent(self):
        """Get a random user agent to avoid blocking"""
        return random.choice(self.user_agents)

    def _get_news_api(self, ticker: str, company_name: str) -> List[NewsItem]:
        """Get news from NewsAPI.org"""
        if not self.news_api_key:
            return []  # Skip if no API key
        
        url = "https://newsapi.org/v2/everything"
        query = f"{company_name} OR {ticker}"
        
        params = {
            "q": query,
            "apiKey": self.news_api_key,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                return []
            
            data = response.json()
            news_items = []
            
            if data.get("articles"):
                for article in data["articles"]:
                    # Filter for relevance
                    title = article.get("title", "").lower()
                    description = article.get("description", "").lower()
                    
                    if ticker.lower() in title or company_name.lower() in title or \
                       ticker.lower() in description or company_name.lower() in description:
                        news_items.append(NewsItem(
                            title=article.get("title", ""),
                            description=article.get("description", ""),
                            source="NewsAPI: " + article.get("source", {}).get("name", "Unknown"),
                            url=article.get("url", ""),
                            published_at=article.get("publishedAt", "")
                        ))
            
            return news_items
        except Exception as e:
            print(f"Error fetching from NewsAPI: {str(e)}")
            return []

    def _get_yahoo_finance(self, ticker: str, company_name: str) -> List[NewsItem]:
        """Get news from Yahoo Finance"""
        headers = {"User-Agent": self._get_random_user_agent()}
        url = f"https://finance.yahoo.com/quote/{ticker}/news"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, "html.parser")
            news_items = []
            
            # Extract news items from Yahoo Finance
            articles = soup.select('div[data-test="CARD"] h3')
            for article in articles[:5]:  # Limit to top 5
                title = article.text.strip()
                link_tag = article.find_parent('a')
                link = "https://finance.yahoo.com" + link_tag['href'] if link_tag and 'href' in link_tag.attrs else None
                
                news_items.append(NewsItem(
                    title=title,
                    description="",  # Yahoo doesn't show description in list view
                    source="Yahoo Finance",
                    url=link,
                    published_at=datetime.now().isoformat()
                ))
            
            return news_items
        except Exception as e:
            print(f"Error fetching from Yahoo Finance: {str(e)}")
            return []

    def _get_market_watch(self, ticker: str, company_name: str) -> List[NewsItem]:
        """Get news from MarketWatch"""
        headers = {"User-Agent": self._get_random_user_agent()}
        url = f"https://www.marketwatch.com/investing/stock/{ticker.lower()}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, "html.parser")
            news_items = []
            
            # Extract news items from MarketWatch
            articles = soup.select('.article__content')
            for article in articles[:5]:  # Limit to top 5
                title_tag = article.select_one('.article__headline')
                title = title_tag.text.strip() if title_tag else ""
                
                link_tag = article.select_one('a.link')
                link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else None
                
                if title:
                    news_items.append(NewsItem(
                        title=title,
                        description="",
                        source="MarketWatch",
                        url=link,
                        published_at=datetime.now().isoformat()
                    ))
            
            return news_items
        except Exception as e:
            print(f"Error fetching from MarketWatch: {str(e)}")
            return []

    def _get_google_finance(self, ticker: str, company_name: str) -> List[NewsItem]:
        """Get news from Google Finance"""
        headers = {"User-Agent": self._get_random_user_agent()}
        
        # Try to handle different ticker formats
        encoded_ticker = ticker.replace('&', '%26')
        url = f"https://www.google.com/finance/quote/{encoded_ticker}:NSE"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                # Try US market
                url = f"https://www.google.com/finance/quote/{encoded_ticker}:NASDAQ"
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    return []
            
            soup = BeautifulSoup(response.text, "html.parser")
            news_items = []
            
            # Extract news items from Google Finance
            articles = soup.select('div.yY3Lee')
            for article in articles[:5]:  # Limit to top 5
                title_tag = article.select_one('.Yfwt5')
                title = title_tag.text.strip() if title_tag else ""
                
                source_tag = article.select_one('.sfyJob')
                source = source_tag.text.strip() if source_tag else "Google Finance"
                
                link_tag = article.parent
                link = "https://www.google.com" + link_tag['href'] if link_tag and 'href' in link_tag.attrs else None
                
                if title:
                    news_items.append(NewsItem(
                        title=title,
                        description="",
                        source=f"Google Finance: {source}",
                        url=link,
                        published_at=datetime.now().isoformat()
                    ))
            
            return news_items
        except Exception as e:
            print(f"Error fetching from Google Finance: {str(e)}")
            return []

    def get_company_news(self, ticker: str, company_name: str) -> List[NewsItem]:
        """
        Get news for a company from multiple sources
        """
        all_news = []
        
        # Use ThreadPoolExecutor to fetch from multiple sources in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks
            future_to_source = {
                executor.submit(source, ticker, company_name): source.__name__
                for source in self.news_sources
            }
            
            # Collect results as they complete
            for future in future_to_source:
                try:
                    news_items = future.result()
                    all_news.extend(news_items)
                except Exception as e:
                    print(f"Error in {future_to_source[future]}: {str(e)}")
        
        # Add sentiment analysis to the news items
        for item in all_news:
            item.sentiment = self._analyze_sentiment(item.title)
        
        # Remove duplicates by title
        unique_news = {}
        for item in all_news:
            if item.title not in unique_news:
                unique_news[item.title] = item
        
        # Return the list of unique news items, prioritizing those with sentiment
        return list(unique_news.values())
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple rule-based sentiment analysis"""
        positive_words = [
            "up", "rise", "gain", "profit", "growth", "positive", "surge",
            "increase", "higher", "rally", "bullish", "outperform", "beat",
            "exceed", "upgrade", "strong", "top", "soar", "jump"
        ]
        
        negative_words = [
            "down", "fall", "drop", "loss", "decline", "negative", "plunge",
            "decrease", "lower", "slip", "bearish", "underperform", "miss",
            "downgrade", "weak", "bottom", "sink", "crash"
        ]
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return "Positive"
        elif neg_count > pos_count:
            return "Negative"
        else:
            return "Neutral"

    def get_market_data(self, ticker: str) -> Dict[str, Any]:
        """Get current market data for a stock"""
        # Try Yahoo Finance API
        headers = {"User-Agent": self._get_random_user_agent()}
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return {}
            
            data = response.json()
            result = data.get('chart', {}).get('result', [])
            if not result:
                return {}
            
            quote = result[0].get('indicators', {}).get('quote', [{}])[0]
            meta = result[0].get('meta', {})
            
            return {
                "current_price": meta.get('regularMarketPrice'),
                "previous_close": meta.get('previousClose'),
                "open_price": quote.get('open', [None])[-1],
                "high_price": quote.get('high', [None])[-1],
                "low_price": quote.get('low', [None])[-1],
                "volume": quote.get('volume', [None])[-1],
                "currency": meta.get('currency'),
                "exchange": meta.get('exchangeName')
            }
        except Exception as e:
            print(f"Error fetching market data: {str(e)}")
            return {}


# For testing
if __name__ == "__main__":
    fetcher = MultiFetchNewsProvider()
    news = fetcher.get_company_news("RELIANCE", "Reliance Industries Ltd")
    print(f"Found {len(news)} news items for Reliance Industries")
    for item in news:
        print(f"- {item.title} ({item.source})")
        print(f"  Sentiment: {item.sentiment}")
        print(f"  URL: {item.url}")
        print("")
        
    # Test market data
    market_data = fetcher.get_market_data("RELIANCE.NS")
    print("\nMarket Data:")
    for key, value in market_data.items():
        print(f"{key}: {value}") 