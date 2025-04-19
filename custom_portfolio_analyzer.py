#!/usr/bin/env python3
"""
Example of using the Portfolio Analyzer as a library in a custom application
"""

from portfolio_analyzer import PortfolioAnalyzer, Stock
from typing import List
import json
from datetime import datetime

def analyze_custom_portfolio():
    """
    Example function showing how to use the portfolio analyzer 
    with your own custom portfolio data
    """
    print("Custom Portfolio Analysis Example")
    print("=================================")
    
    # Create a custom portfolio with your stocks
    custom_portfolio: List[Stock] = [
        Stock(
            name="Apple Inc", 
            ticker="AAPL", 
            sector="Technology",
            quantity=10,
            average_price=150.25,
            current_price=175.50
        ),
        Stock(
            name="Microsoft Corporation", 
            ticker="MSFT", 
            sector="Technology",
            quantity=5,
            average_price=250.75,
            current_price=280.25
        ),
        Stock(
            name="Tesla Inc", 
            ticker="TSLA", 
            sector="Automotive",
            quantity=8,
            average_price=180.50,
            current_price=220.75
        ),
        Stock(
            name="Amazon.com Inc", 
            ticker="AMZN", 
            sector="E-Commerce",
            quantity=3,
            average_price=140.25,
            current_price=180.50
        )
    ]
    
    # Initialize the analyzer
    analyzer = PortfolioAnalyzer()
    
    # Analyze the custom portfolio
    print(f"\nAnalyzing custom portfolio of {len(custom_portfolio)} stocks...")
    results = analyzer.analyze_portfolio(custom_portfolio)
    
    # Save to JSON
    output_file = "custom_portfolio_analysis.json"
    results.to_json(output_file)
    
    print(f"Analysis complete! Results saved to {output_file}")
    
    # Print summary
    print("\nAnalysis Summary:")
    for stock in results.stocks:
        print(f"\n{stock.stock} ({stock.ticker}) - {stock.impact}:")
        print(f"  {stock.news_summary}")
        
        # Display URLs for additional news
        if stock.additional_news:
            print("\n  Additional news:")
            for i, news in enumerate(stock.additional_news, 1):
                if news.url:
                    print(f"  {i}. {news.title}")
                    print(f"     URL: {news.url}")
    
    return results

if __name__ == "__main__":
    # Run the custom portfolio analysis
    analyze_custom_portfolio() 