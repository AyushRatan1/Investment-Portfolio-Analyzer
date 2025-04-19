import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables
API_KEY = os.getenv("NEWS_API_KEY")

def get_stock_news(ticker, company_name, sector):
    """
    Get recent news for a specific stock using News API
    """
    # Base URL for News API
    url = "https://newsapi.org/v2/everything"
    
    # Create query with company name and ticker
    query = f"{company_name} OR {ticker}"
    
    # Parameters for the API request
    params = {
        "q": query,
        "apiKey": API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5  # Limit to 5 recent articles
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200 and data.get("articles"):
            # Get the most recent relevant article
            for article in data["articles"]:
                title = article.get("title", "").lower()
                description = article.get("description", "").lower()
                content = article.get("content", "").lower()
                
                # Check if the article is relevant to the company
                if (company_name.lower() in title or ticker.lower() in title or
                    company_name.lower() in description or ticker.lower() in description):
                    summary = article.get("title")
                    return summary
            
            # If no specific company news was found, check for sector news
            sector_query = f"{sector} industry news"
            sector_params = {
                "q": sector_query,
                "apiKey": API_KEY,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 3
            }
            
            sector_response = requests.get(url, params=sector_params)
            sector_data = sector_response.json()
            
            if sector_response.status_code == 200 and sector_data.get("articles"):
                # Get sector news
                article = sector_data["articles"][0]
                return f"Sector news: {article.get('title')}"
            
            return f"No significant news found for {company_name} or {sector} sector."
        else:
            return f"No recent news found for {company_name}."
    
    except Exception as e:
        return f"Error fetching news: {str(e)}"

def assess_impact(news_summary):
    """
    Assess the impact of news as Positive, Negative, or Neutral
    Simple keyword-based assessment
    """
    positive_keywords = [
        "growth", "profit", "increase", "rise", "up", "gain", "positive",
        "success", "launch", "partnership", "acquisition", "beat", "exceeds",
        "innovation", "deal", "agreement", "improvement", "boost", "soar"
    ]
    
    negative_keywords = [
        "decline", "drop", "fall", "down", "loss", "negative", "cut",
        "reduce", "weak", "miss", "fail", "risk", "concern", "trouble",
        "investigation", "lawsuit", "regulatory", "delay", "warning"
    ]
    
    news_lower = news_summary.lower()
    
    positive_count = sum(1 for word in positive_keywords if word in news_lower)
    negative_count = sum(1 for word in negative_keywords if word in news_lower)
    
    if positive_count > negative_count:
        return "Positive"
    elif negative_count > positive_count:
        return "Negative"
    else:
        return "Neutral"

def analyze_stocks(holdings):
    """
    Analyze a list of stock holdings and return insights
    """
    results = []
    
    for holding in holdings:
        name = holding.get("name")
        ticker = holding.get("ticker")
        sector = holding.get("sector")
        
        # Get news for the stock
        news_summary = get_stock_news(ticker, name, sector)
        
        # Assess the impact
        impact = assess_impact(news_summary)
        
        # Add to results
        results.append({
            "stock": name,
            "news_summary": news_summary,
            "impact": impact
        })
    
    return results

def main():
    # Check if API key is available
    if not API_KEY:
        print("Error: NEWS_API_KEY not found in environment variables.")
        print("Please obtain an API key from newsapi.org and set it as NEWS_API_KEY in a .env file.")
        return
    
    try:
        # Read input holdings
        with open("holdings.json", "r") as f:
            holdings = json.load(f)
        
        # Analyze stocks
        results = analyze_stocks(holdings)
        
        # Write results to file
        with open("analysis_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"Analysis complete. Results saved to analysis_results.json")
        
        # Also print results to console
        print("\nStock Analysis Results:")
        for result in results:
            print(f"\n{result['stock']} ({result['impact']}):")
            print(f"  {result['news_summary']}")
    
    except FileNotFoundError:
        print("Error: holdings.json file not found.")
        print("Please create a holdings.json file with your stock holdings.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in holdings.json.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 