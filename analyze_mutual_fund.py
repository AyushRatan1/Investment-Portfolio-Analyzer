#!/usr/bin/env python3
"""
Interactive Mutual Fund Analyzer
This script allows users to choose a mutual fund file to analyze
"""

import os
import sys
from mutual_fund_analyzer import MutualFundAnalyzer

def list_mutual_fund_files():
    """List mutual fund files in the samples directory"""
    samples_dir = "samples"
    files = []
    
    if os.path.exists(samples_dir):
        for file in os.listdir(samples_dir):
            if file.endswith(".xlsx"):
                files.append(os.path.join(samples_dir, file))
    
    return files

def select_file(files):
    """Let user select a file or provide their own"""
    print("\nAvailable mutual fund files:")
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
    """Main function for interactive mutual fund analysis"""
    print("=" * 60)
    print("Mutual Fund Portfolio Analyzer with AI Impact Assessment".center(60))
    print("=" * 60)
    
    # Check for API keys
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    news_api_key = os.getenv("NEWS_API_KEY")
    llm_api_key = os.getenv("LLM_API_KEY", "xai-L9NtX3VBbiKDNisc12yssrysUYw3KZt4JFlKzfcmLeJyEWums01fMVPmw2LspuqQcq9I1iL42ITnthVq")
    
    if not news_api_key:
        print("\nWARNING: No NewsAPI key found in .env file.")
        print("You need a NewsAPI.org API key to fetch news.")
        print("Please add your key to the .env file: NEWS_API_KEY=your_key_here")
        
        setup_key = input("\nWould you like to enter your NewsAPI key now? (y/n): ").lower()
        if setup_key == 'y':
            news_api_key = input("Enter your NewsAPI.org API key: ").strip()
            
            # Update or create .env file
            env_contents = f"NEWS_API_KEY={news_api_key}\nLLM_API_KEY={llm_api_key}"
            with open(".env", "w") as f:
                f.write(env_contents)
            
            print("API key saved to .env file.")
        else:
            print("News analysis may be limited without an API key.")
    
    # Check if we have sample files, if not, offer to create them
    mutual_fund_files = list_mutual_fund_files()
    
    if not mutual_fund_files:
        print("\nNo sample mutual fund files found.")
        create_samples = input("Would you like to create sample mutual fund files for testing? (y/n): ").lower()
        
        if create_samples == 'y':
            print("\nCreating sample mutual fund files...")
            from create_sample_mutual_fund import create_index_fund_sample, create_technology_fund_sample, create_banking_fund_sample
            
            create_index_fund_sample()
            create_technology_fund_sample()
            create_banking_fund_sample()
            
            print("Sample files created successfully.")
            mutual_fund_files = list_mutual_fund_files()
        else:
            print("Please provide your own mutual fund Excel file.")
            while True:
                file_path = input("Enter the full path to your Excel file: ").strip()
                if os.path.exists(file_path) and file_path.endswith(".xlsx"):
                    selected_file = file_path
                    break
                else:
                    print("File not found or not an Excel file. Please try again.")
            
            if not selected_file:
                print("No valid file provided. Exiting.")
                return
    else:
        # Let user select a file
        selected_file = select_file(mutual_fund_files)
    
    # Create and run the analyzer
    try:
        print(f"\nAnalyzing mutual fund: {os.path.basename(selected_file)}")
        
        # Create visualizations directory if it doesn't exist
        os.makedirs("visualizations", exist_ok=True)
        
        # Initialize analyzer with API keys
        analyzer = MutualFundAnalyzer(news_api_key=news_api_key, llm_api_key=llm_api_key)
        
        # Analyze the mutual fund
        results = analyzer.analyze_from_excel(selected_file)
        
        # Generate output filename based on input
        base_name = os.path.basename(selected_file).split('.')[0]
        output_path = f"{base_name}_analysis.json"
        
        # Save results
        results.to_json(output_path)
        
        # Generate visualizations
        print("\nGenerating visualizations...")
        viz_paths = results.generate_visualizations("visualizations")
        
        # Display results summary
        print(f"\nMutual Fund Analysis Complete!")
        print(f"Results saved to {output_path}")
        print(f"Visualizations saved to visualizations/ directory")
        
        # Print fund summary
        print(f"\n{results.fund_name} - Analysis Summary")
        print(f"Holdings: {results.holdings_count}")
        
        # Sector allocation (top 5)
        print("\nTop Sectors:")
        for sector, pct in sorted(results.sector_exposure.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"{sector}: {pct:.2f}%")
        
        # Top 5 holdings
        print("\nTop 5 Holdings:")
        for i, holding in enumerate(results.top_holdings[:5], 1):
            print(f"{i}. {holding.name}: {holding.percentage:.2f}%")
        
        # News impact summary
        impact_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        for analysis in results.stock_analyses:
            impact_counts[analysis.impact] += 1
        
        print("\nNews Impact Summary:")
        total = sum(impact_counts.values())
        for impact, count in impact_counts.items():
            if total > 0:
                percentage = (count / total) * 100
                print(f"{impact}: {count} holdings ({percentage:.1f}%)")
        
        # Ask if user wants to see AI analysis
        show_ai = input("\nShow detailed AI analysis? (y/n): ").lower()
        if show_ai == 'y':
            print("\nAI Impact Analysis:")
            print(f"Overall Impact: {results.llm_analysis.impact}")
            print(f"\nSummary: {results.llm_analysis.summary}")
            
            print("\nRecommendations:")
            for i, rec in enumerate(results.llm_analysis.recommendations, 1):
                print(f"{i}. {rec}")
            
            print("\nRisks:")
            for i, risk in enumerate(results.llm_analysis.risks, 1):
                print(f"{i}. {risk}")
            
            print("\nOpportunities:")
            for i, opp in enumerate(results.llm_analysis.opportunities, 1):
                print(f"{i}. {opp}")
        
        # Ask if user wants to see news for specific holdings
        show_news = input("\nShow news for specific holdings? (y/n): ").lower()
        if show_news == 'y':
            while True:
                print("\nAvailable holdings:")
                for i, analysis in enumerate(results.stock_analyses[:15], 1):
                    print(f"{i}. {analysis.stock} ({analysis.impact})")
                
                print("0. Exit")
                
                try:
                    holding_choice = int(input("\nEnter holding number to view news (0 to exit): "))
                    
                    if holding_choice == 0:
                        break
                    
                    if 1 <= holding_choice <= len(results.stock_analyses[:15]):
                        selected = results.stock_analyses[holding_choice - 1]
                        
                        print(f"\nNews for {selected.stock}:")
                        print(f"Main: {selected.news_summary}")
                        
                        if selected.additional_news:
                            print("\nAdditional News:")
                            for i, news in enumerate(selected.additional_news, 1):
                                print(f"{i}. {news.title}")
                                if news.url:
                                    print(f"   URL: {news.url}")
                    else:
                        print("Invalid choice. Please try again.")
                
                except ValueError:
                    print("Please enter a number.")
        
        print("\nThank you for using the Mutual Fund Analyzer with AI Impact Assessment!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 