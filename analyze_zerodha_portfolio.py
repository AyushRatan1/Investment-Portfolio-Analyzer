#!/usr/bin/env python3
"""
Script to analyze a Zerodha-format portfolio
"""

from portfolio_analyzer import PortfolioAnalyzer
import os

def main():
    """Main function to analyze a Zerodha-format portfolio"""
    # Path to the Zerodha-format portfolio file
    portfolio_file = "samples/sample_zerodha_portfolio.xlsx"
    
    # Create analyzer instance
    analyzer = PortfolioAnalyzer()
    
    # Analyze the portfolio
    print(f"Analyzing Zerodha-format portfolio: {portfolio_file}")
    results = analyzer.analyze_from_excel(portfolio_file)
    
    # Save results to JSON
    output_path = "zerodha_portfolio_analysis.json"
    results.to_json(output_path)
    
    # Display results summary
    print(f"\nPortfolio Analysis Complete!")
    print(f"Results saved to {output_path}")
    
    print("\nAnalysis Summary:")
    for stock in results.stocks:
        print(f"\n{stock.stock} ({stock.ticker}) - {stock.impact}:")
        print(f"  {stock.news_summary}")
        
        if stock.additional_news:
            print("  Additional news headlines:")
            for i, news in enumerate(stock.additional_news, 1):
                print(f"  {i}. {news.title}")

if __name__ == "__main__":
    main() 