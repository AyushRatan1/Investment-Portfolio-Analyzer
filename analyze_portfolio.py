#!/usr/bin/env python3
"""
Interactive Portfolio Analyzer
This script allows users to choose a portfolio file to analyze
"""

import os
import sys
from portfolio_analyzer import PortfolioAnalyzer

def list_portfolio_files():
    """List portfolio files in the samples directory"""
    samples_dir = "samples"
    files = []
    
    if os.path.exists(samples_dir):
        for file in os.listdir(samples_dir):
            if file.endswith(".xlsx"):
                files.append(os.path.join(samples_dir, file))
    
    return files

def select_file(files):
    """Let user select a file or provide their own"""
    print("\nAvailable portfolio files:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {os.path.basename(file)}")
    
    print(f"{len(files) + 1}. Use my own file (provide path)")
    
    while True:
        try:
            choice = input("\nEnter your choice (number): ")
            choice = int(choice.strip())
            
            if 1 <= choice <= len(files):
                return files[choice - 1]
            elif choice == len(files) + 1:
                while True:
                    file_path = input("Enter the full path to your Excel file: ").strip()
                    if os.path.exists(file_path) and file_path.endswith(".xlsx"):
                        return file_path
                    else:
                        print("File not found or not an Excel file. Please try again.")
            else:
                print("Invalid choice. Please try again.")
        
        except ValueError:
            print("Please enter a number.")

def main():
    """Main function for interactive portfolio analysis"""
    print("=" * 50)
    print("Portfolio News Analyzer".center(50))
    print("=" * 50)
    
    # Check for API key
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    api_key = os.getenv("NEWS_API_KEY")
    
    if not api_key:
        print("\nWARNING: No NewsAPI key found in .env file.")
        print("You need a NewsAPI.org API key to fetch news.")
        print("Please add your key to the .env file: NEWS_API_KEY=your_key_here")
        
        setup_key = input("\nWould you like to enter your API key now? (y/n): ").lower()
        if setup_key == 'y':
            api_key = input("Enter your NewsAPI.org API key: ").strip()
            with open(".env", "w") as f:
                f.write(f"NEWS_API_KEY={api_key}")
            print("API key saved to .env file.")
        else:
            print("You can add your API key later by editing the .env file.")
            return
    
    # List portfolio files
    portfolio_files = list_portfolio_files()
    
    if not portfolio_files:
        print("\nNo sample portfolio files found.")
        print("Please create a sample portfolio first by running:")
        print("python3 create_sample_portfolio.py")
        return
    
    # Let user select a file
    selected_file = select_file(portfolio_files)
    
    # Create and run the analyzer
    try:
        print(f"\nAnalyzing portfolio: {os.path.basename(selected_file)}")
        
        analyzer = PortfolioAnalyzer(api_key=api_key)
        results = analyzer.analyze_from_excel(selected_file)
        
        # Generate output filename based on input
        base_name = os.path.basename(selected_file).split('.')[0]
        output_path = f"{base_name}_analysis.json"
        
        # Save results
        results.to_json(output_path)
        
        # Display results summary
        print(f"\nPortfolio Analysis Complete!")
        print(f"Results saved to {output_path}")
        
        # Print number of stocks analyzed
        stock_count = len(results.stocks)
        print(f"\nAnalyzed {stock_count} stocks:")
        
        # Counts by impact
        impact_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        for stock in results.stocks:
            impact_counts[stock.impact] += 1
        
        # Print impact summary
        print(f"  Positive: {impact_counts['Positive']}")
        print(f"  Negative: {impact_counts['Negative']}")
        print(f"  Neutral: {impact_counts['Neutral']}")
        
        # Ask if user wants to see detailed results
        show_details = input("\nShow detailed results? (y/n): ").lower()
        if show_details == 'y':
            print("\nDetailed Analysis Results:")
            for stock in results.stocks:
                print(f"\n{stock.stock} ({stock.ticker}) - {stock.impact}:")
                print(f"  {stock.news_summary}")
                
                if stock.additional_news:
                    print("  Additional news headlines:")
                    for i, news in enumerate(stock.additional_news, 1):
                        print(f"  {i}. {news.title}")
        
        print("\nThank you for using the Portfolio News Analyzer!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 