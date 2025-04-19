#!/usr/bin/env python3
"""
Example script to analyze your portfolio
"""

from portfolio_analyzer import PortfolioAnalyzer
import os

def main():
    """Main function to analyze a sample portfolio"""
    # Path to your portfolio Excel file
    samples_dir = "samples"
    
    # List available sample files
    print("Available sample portfolio files:")
    for i, file in enumerate(os.listdir(samples_dir), 1):
        if file.endswith(".xlsx"):
            print(f"{i}. {file}")
    
    # Create analyzer instance
    analyzer = PortfolioAnalyzer()
    
    # Default to the Groww-like sample
    portfolio_file = os.path.join(samples_dir, "sample_portfolio.xlsx")
    
    # Analyze the portfolio
    results = analyzer.analyze_from_excel(portfolio_file)
    
    # Save results to JSON
    output_path = "my_portfolio_analysis.json"
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