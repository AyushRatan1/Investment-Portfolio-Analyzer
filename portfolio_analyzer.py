import json
import os
import sys
import requests
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Import the new multi-source news fetcher
try:
    from news_fetcher import MultiFetchNewsProvider, NewsItem as FetcherNewsItem
    MULTI_FETCHER_AVAILABLE = True
except ImportError:
    MULTI_FETCHER_AVAILABLE = False

# Load environment variables
load_dotenv()

# Get API key from environment variables
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Define Pydantic models for our data structures
class Stock(BaseModel):
    """Model for a stock in the portfolio"""
    name: str
    ticker: str
    sector: Optional[str] = None
    quantity: Optional[float] = None
    average_price: Optional[float] = None
    current_price: Optional[float] = None
    
    @validator('ticker')
    def ticker_uppercase(cls, v):
        return v.upper() if isinstance(v, str) else v

class NewsItem(BaseModel):
    """Model for a news item related to a stock"""
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[str] = None

class StockAnalysis(BaseModel):
    """Model for stock analysis result"""
    stock: str
    ticker: str
    sector: Optional[str] = None
    news_summary: str
    impact: str
    additional_news: Optional[List[NewsItem]] = Field(default_factory=list)

class PortfolioAnalysis(BaseModel):
    """Model for the entire portfolio analysis"""
    stocks: List[StockAnalysis]
    timestamp: str
    
    def to_json(self, filepath=None):
        """Convert the analysis to JSON"""
        data = self.model_dump(mode='json')
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        return data

class PortfolioAnalyzer:
    """AI agent to analyze a portfolio of stocks"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or NEWS_API_KEY
        if not self.api_key:
            print("Warning: No NEWS_API_KEY found. Please set it in your .env file.")
    
    def extract_portfolio_from_excel(self, filepath: str) -> List[Stock]:
        """
        Extract portfolio data from an Excel file
        Tries to handle various formats exported from platforms like Groww
        """
        try:
            # Read the Excel file
            df = pd.read_excel(filepath)
            
            # Check for common column names in various formats
            # Map of standard column names to possible variations
            column_maps = {
                'name': ['Company Name', 'Name', 'Stock', 'Company', 'Security Name', 'Symbol Name', 'Instrument'],
                'ticker': ['Ticker', 'Symbol', 'Stock Symbol', 'NSE Symbol', 'BSE Symbol', 'ISIN', 'Security Code', 'Tradingsymbol'],
                'sector': ['Sector', 'Industry', 'Category', 'Segment'],
                'quantity': ['Qty', 'Quantity', 'Shares', 'Holding', 'Units', 'Volume', 'Qty.'],
                'average_price': ['Avg. Cost', 'Average Price', 'Buy Price', 'Cost Price', 'Avg Cost', 'Purchase Price', 'Avg.'],
                'current_price': ['LTP', 'Last Price', 'Current Price', 'Market Price', 'CMP', 'Close Price']
            }
            
            # Create a mapping of existing columns to standard names
            column_mapping = {}
            for std_name, variations in column_maps.items():
                for col in df.columns:
                    if col in variations or any(var.lower() == col.lower() for var in variations):
                        column_mapping[col] = std_name
                        break
            
            # Rename columns based on the mapping
            if column_mapping:
                df = df.rename(columns=column_mapping)
            
            # Ensure we have at least name and ticker
            required_cols = ['name', 'ticker']
            if not all(col in df.columns for col in required_cols):
                # Try to infer missing columns if possible
                if 'name' not in df.columns and 'ticker' in df.columns:
                    df['name'] = df['ticker']  # Use ticker as name if missing
                elif 'ticker' not in df.columns and 'name' in df.columns:
                    df['ticker'] = df['name']  # Use name as ticker if missing
                else:
                    return []  # Can't proceed without essential info
            
            # Convert DataFrame to list of Stock models
            stocks = []
            for _, row in df.iterrows():
                stock_data = {}
                for col in column_maps.keys():
                    if col in df.columns:
                        stock_data[col] = row[col]
                
                # Only include stocks with valid name and ticker
                if 'name' in stock_data and 'ticker' in stock_data:
                    stocks.append(Stock(**stock_data))
            
            return stocks
        
        except Exception as e:
            print(f"Error extracting portfolio: {str(e)}")
            return []
    
    def get_stock_news(self, stock: Stock) -> List[NewsItem]:
        """
        Get recent news for a specific stock using multiple sources
        """
        # Try the multi-source fetcher first if available
        if MULTI_FETCHER_AVAILABLE:
            try:
                fetcher = MultiFetchNewsProvider(api_key=self.api_key)
                news_items = fetcher.get_company_news(stock.ticker, stock.name)
                
                # Convert fetcher news items to our format
                if news_items:
                    return [NewsItem(
                        title=item.title,
                        description=item.description or "",
                        source=item.source or "External Source",
                        url=item.url,
                        published_at=item.published_at
                    ) for item in news_items]
                
                # If no news found from multi-source fetcher, try to get market data
                market_data = fetcher.get_market_data(stock.ticker)
                if market_data and market_data.get('current_price'):
                    # Update stock object with market data
                    stock.current_price = market_data.get('current_price')
                    
                    # Create a news item with the market data
                    return [NewsItem(
                        title=f"{stock.name} ({stock.ticker}) current price: {market_data.get('current_price')}",
                        description=f"Open: {market_data.get('open_price')} | High: {market_data.get('high_price')} | Low: {market_data.get('low_price')} | Volume: {market_data.get('volume')}",
                        source="Market Data",
                        url=None,
                        published_at=datetime.now().isoformat()
                    )]
            except Exception as e:
                print(f"Error using multi-source fetcher: {str(e)}")
                # Continue with fallback methods if multi-source fetcher fails
        
        # Fallback to NewsAPI if API key is available
        if self.api_key:
            # Base URL for News API
            url = "https://newsapi.org/v2/everything"
            
            # Create query with company name and ticker
            query = f"{stock.name} OR {stock.ticker}"
            if stock.sector:
                query += f" OR ({stock.ticker} AND {stock.sector})"
            
            # Parameters for the API request
            params = {
                "q": query,
                "apiKey": self.api_key,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 5  # Limit to 5 recent articles
            }
            
            try:
                response = requests.get(url, params=params)
                data = response.json()
                
                if response.status_code == 200 and data.get("articles"):
                    news_items = []
                    for article in data["articles"]:
                        # Check if the article is relevant to the company
                        title = article.get("title", "").lower()
                        description = article.get("description", "").lower()
                        
                        relevance_score = 0
                        if stock.name.lower() in title or stock.ticker.lower() in title:
                            relevance_score += 3
                        if stock.name.lower() in description or stock.ticker.lower() in description:
                            relevance_score += 2
                        if stock.sector and stock.sector.lower() in (title + " " + description).lower():
                            relevance_score += 1
                        
                        # Only include relevant news
                        if relevance_score > 0:
                            news_items.append(NewsItem(
                                title=article.get("title", ""),
                                description=article.get("description", ""),
                                source=article.get("source", {}).get("name", ""),
                                url=article.get("url", ""),
                                published_at=article.get("publishedAt", "")
                            ))
                    
                    # If we found relevant news, return it
                    if news_items:
                        return news_items
                    
                    # If no relevant news, create a fallback news item with market data placeholder
                    return [self.create_fallback_news_item(stock)]
                
                # If API call failed or no articles returned, use fallback
                return [self.create_fallback_news_item(stock)]
            
            except Exception as e:
                print(f"Error fetching news for {stock.name}: {str(e)}")
                return [self.create_fallback_news_item(stock, error=str(e))]
        else:
            # Fallback for when API key is not provided
            return [self.create_fallback_news_item(stock, no_api=True)]

    def create_fallback_news_item(self, stock: Stock, error=None, no_api=False) -> NewsItem:
        """Create a fallback news item with some basic market information"""
        # Determine a basic fallback message based on stock information
        current_price = stock.current_price
        avg_price = stock.average_price
        
        if error:
            title = f"Error fetching news for {stock.name}: {error}"
            desc = "Please check your API key or network connection."
        elif no_api:
            title = f"Using basic market data for {stock.name} (API key not provided)"
            desc = "To get real news updates, please provide a NewsAPI key or install additional dependencies for the multi-source news fetcher."
        elif current_price and avg_price:
            if current_price > avg_price:
                pct_change = ((current_price - avg_price) / avg_price) * 100
                title = f"{stock.name} is trading {pct_change:.2f}% above your average buy price"
                desc = f"Current price: {current_price} | Average buy price: {avg_price}"
            elif current_price < avg_price:
                pct_change = ((avg_price - current_price) / avg_price) * 100
                title = f"{stock.name} is trading {pct_change:.2f}% below your average buy price"
                desc = f"Current price: {current_price} | Average buy price: {avg_price}"
            else:
                title = f"{stock.name} is trading at your average buy price"
                desc = f"Current price: {current_price} | Average buy price: {avg_price}"
        elif current_price:
            title = f"Current price of {stock.name}: {current_price}"
            desc = "No price change data available."
        else:
            # Most basic fallback
            title = f"Basic information for {stock.name} ({stock.ticker})"
            desc = f"Sector: {stock.sector or 'Unknown'}"
            if stock.quantity:
                desc += f" | Quantity held: {stock.quantity}"
        
        return NewsItem(
            title=title,
            description=desc,
            source="System Analysis",
            url=None,
            published_at=datetime.now().isoformat()
        )
    
    def assess_impact(self, news_items: List[NewsItem]) -> str:
        """
        Assess the impact of news as Positive, Negative, or Neutral
        Based on sentiment analysis of news titles and descriptions
        """
        if not news_items:
            return "Neutral"
        
        # Check if this is a fallback news item from our system
        if len(news_items) == 1 and news_items[0].source == "System Analysis":
            # Parse the title to check if it contains information about price changes
            title = news_items[0].title.lower()
            if "above your average" in title:
                return "Positive"
            elif "below your average" in title:
                return "Negative"
            else:
                return "Neutral"
            
        positive_keywords = [
            "growth", "profit", "increase", "rise", "up", "gain", "positive",
            "success", "launch", "partnership", "acquisition", "beat", "exceeds",
            "surpass", "improvement", "innovation", "progress", "win", "award"
        ]
        
        negative_keywords = [
            "loss", "decline", "decrease", "fall", "down", "drop", "negative",
            "failure", "lawsuit", "investigation", "fine", "penalty", "miss",
            "below", "concern", "risk", "threat", "weak", "cut", "layoff"
        ]
        
        # Calculate sentiment scores
        positive_score = 0
        negative_score = 0
        
        for news in news_items:
            text = (news.title + " " + (news.description or "")).lower()
            
            # Count keyword occurrences
            for keyword in positive_keywords:
                if keyword in text:
                    positive_score += 1
            
            for keyword in negative_keywords:
                if keyword in text:
                    negative_score += 1
        
        # Determine overall sentiment
        if positive_score > negative_score:
            return "Positive"
        elif negative_score > positive_score:
            return "Negative"
        else:
            return "Neutral"
    
    def get_sector_news(self, sector: str) -> List[NewsItem]:
        """Get news related to a sector if no specific company news found"""
        if not self.api_key or not sector:
            return []
            
        url = "https://newsapi.org/v2/everything"
        query = f"{sector} sector industry market"
        
        params = {
            "q": query,
            "apiKey": self.api_key,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 3
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code == 200 and data.get("articles"):
                return [NewsItem(
                    title=f"Sector news: {article.get('title', '')}",
                    description=article.get("description", ""),
                    source=article.get("source", {}).get("name", ""),
                    url=article.get("url", ""),
                    published_at=article.get("publishedAt", "")
                ) for article in data["articles"]]
            
            return []
        
        except Exception as e:
            print(f"Error fetching sector news for {sector}: {str(e)}")
            return []
    
    def analyze_portfolio(self, stocks: List[Stock]) -> PortfolioAnalysis:
        """
        Analyze a portfolio of stocks and return insights
        """
        analysis_results = []
        
        for stock in stocks:
            # Get news for the stock
            news_items = self.get_stock_news(stock)
            
            # If no specific company news found, try to get sector news
            if not news_items and stock.sector:
                sector_news = self.get_sector_news(stock.sector)
                if sector_news:
                    news_items = sector_news
            
            # Assess the impact
            impact = self.assess_impact(news_items)
            
            # Main news summary (first item or default message)
            if news_items:
                main_news = news_items[0].title
                additional_news = news_items[1:] if len(news_items) > 1 else []
            else:
                main_news = f"No significant news found for {stock.name}"
                additional_news = []
            
            # Add to results
            analysis_results.append(StockAnalysis(
                stock=stock.name,
                ticker=stock.ticker,
                sector=stock.sector,
                news_summary=main_news,
                impact=impact,
                additional_news=additional_news
            ))
        
        # Create the portfolio analysis
        return PortfolioAnalysis(
            stocks=analysis_results,
            timestamp=datetime.now().isoformat()
        )
    
    def analyze_from_excel(self, excel_path: str) -> PortfolioAnalysis:
        """
        Read portfolio from Excel and analyze it
        """
        # Extract stocks from Excel
        stocks = self.extract_portfolio_from_excel(excel_path)
        
        if not stocks:
            print(f"No valid stocks found in {excel_path}")
            return PortfolioAnalysis(stocks=[], timestamp=datetime.now().isoformat())
        
        # Analyze the portfolio
        return self.analyze_portfolio(stocks)

def main():
    """Main function to run the portfolio analyzer"""
    # Check if API key is available
    if not NEWS_API_KEY:
        print("Error: NEWS_API_KEY not found in environment variables.")
        print("Please obtain an API key from newsapi.org and set it as NEWS_API_KEY in a .env file.")
        return
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python portfolio_analyzer.py <path_to_excel_file>")
        return
    
    excel_path = sys.argv[1]
    if not os.path.exists(excel_path):
        print(f"Error: File not found: {excel_path}")
        return
    
    try:
        # Create and run the analyzer
        analyzer = PortfolioAnalyzer()
        results = analyzer.analyze_from_excel(excel_path)
        
        # Save results to JSON
        output_path = "portfolio_analysis.json"
        results.to_json(output_path)
        
        print(f"\nPortfolio Analysis Complete!")
        print(f"Results saved to {output_path}")
        
        # Print summary to console
        print("\nAnalysis Summary:")
        for stock in results.stocks:
            print(f"\n{stock.stock} ({stock.ticker}) - {stock.impact}:")
            print(f"  {stock.news_summary}")
            
            if stock.additional_news:
                print("  Additional news headlines:")
                for i, news in enumerate(stock.additional_news, 1):
                    print(f"  {i}. {news.title}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 