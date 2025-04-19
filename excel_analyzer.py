#!/usr/bin/env python3
"""
Excel-to-Excel Portfolio/Mutual Fund Analyzer
This script processes Excel files and outputs analysis results as Excel files
"""

import os
import sys
import pandas as pd
import argparse
from datetime import datetime
from pathlib import Path

# Import the analyzers
from mutual_fund_analyzer import MutualFundAnalyzer
from portfolio_analyzer import PortfolioAnalyzer

def analyze_excel_file(input_file, output_file=None, analysis_type="auto", news_api_key=None):
    """
    Analyze an Excel file and output the results as an Excel file
    
    Args:
        input_file: Path to the input Excel file
        output_file: Path to the output Excel file (optional)
        analysis_type: Type of analysis to perform ("portfolio", "mutual_fund", or "auto")
        news_api_key: NewsAPI key for news analysis
    
    Returns:
        Path to the output Excel file
    """
    # Set API key in environment variable if provided
    if news_api_key:
        os.environ["NEWS_API_KEY"] = news_api_key
    
    # Determine analysis type if set to auto
    if analysis_type == "auto":
        filename = os.path.basename(input_file).lower()
        if "fund" in filename:
            analysis_type = "mutual_fund"
        else:
            analysis_type = "portfolio"
    
    # Set default output filename if not provided
    if not output_file:
        input_name = Path(input_file).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{input_name}_analysis_{timestamp}.xlsx"
    
    print(f"Analyzing {input_file} as {analysis_type}...")
    
    try:
        # Perform the analysis
        if analysis_type == "mutual_fund":
            analyzer = MutualFundAnalyzer(news_api_key=os.getenv("NEWS_API_KEY"))
            results = analyzer.analyze_from_excel(input_file)
            
            # Generate visualizations
            viz_dir = "visualizations"
            os.makedirs(viz_dir, exist_ok=True)
            viz_paths = results.generate_visualizations(viz_dir)
            
            # Create Excel output
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = {
                    "Fund Name": [results.fund_name],
                    "Analysis Date": [results.timestamp],
                    "Holdings Count": [results.holdings_count],
                    "Overall Impact": [results.llm_analysis.impact]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                # Top Holdings sheet
                holdings_data = []
                for holding in results.top_holdings:
                    holdings_data.append({
                        "Company": holding.name,
                        "Ticker": holding.ticker or "N/A",
                        "Sector": holding.sector or "N/A",
                        "% of Fund": holding.percentage
                    })
                pd.DataFrame(holdings_data).to_excel(writer, sheet_name='Top Holdings', index=False)
                
                # Sector Exposure sheet
                sector_data = []
                for sector, percentage in results.sector_exposure.items():
                    sector_data.append({
                        "Sector": sector,
                        "Allocation (%)": percentage
                    })
                pd.DataFrame(sector_data).to_excel(writer, sheet_name='Sector Allocation', index=False)
                
                # News Impact sheet
                news_data = []
                for analysis in results.stock_analyses:
                    news_data.append({
                        "Company": analysis.stock,
                        "Ticker": analysis.ticker,
                        "Impact": analysis.impact,
                        "News Summary": analysis.news_summary
                    })
                pd.DataFrame(news_data).to_excel(writer, sheet_name='News Impact', index=False)
                
                # AI Analysis sheet
                ai_data = {
                    "Summary": [results.llm_analysis.summary],
                    "Impact": [results.llm_analysis.impact]
                }
                ai_df = pd.DataFrame(ai_data)
                ai_df.to_excel(writer, sheet_name='AI Analysis', index=False)
                
                # Recommendations, Risks, Opportunities
                recommendations_df = pd.DataFrame({"Recommendations": results.llm_analysis.recommendations})
                recommendations_df.to_excel(writer, sheet_name='Recommendations', index=False)
                
                risks_df = pd.DataFrame({"Risks": results.llm_analysis.risks})
                risks_df.to_excel(writer, sheet_name='Risks', index=False)
                
                opportunities_df = pd.DataFrame({"Opportunities": results.llm_analysis.opportunities})
                opportunities_df.to_excel(writer, sheet_name='Opportunities', index=False)
            
        else:  # portfolio analysis
            analyzer = PortfolioAnalyzer(api_key=os.getenv("NEWS_API_KEY"))
            results = analyzer.analyze_from_excel(input_file)
            
            # Create Excel output
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = {
                    "Analysis Date": [results.timestamp],
                    "Stocks Count": [len(results.stocks)]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                # Impact summary
                impact_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
                for stock in results.stocks:
                    impact_counts[stock.impact] += 1
                
                impact_df = pd.DataFrame({
                    "Impact": list(impact_counts.keys()),
                    "Count": list(impact_counts.values())
                })
                impact_df.to_excel(writer, sheet_name='Impact Summary', index=False)
                
                # Create a pivot table for sector-based impact analysis
                sector_impact_data = []
                sectors = set()
                for stock in results.stocks:
                    sectors.add(stock.sector or "Unknown")
                    sector_impact_data.append({
                        "Company": stock.stock,
                        "Ticker": stock.ticker,
                        "Sector": stock.sector or "Unknown",
                        "Impact": stock.impact
                    })
                
                if sector_impact_data:
                    sector_impact_df = pd.DataFrame(sector_impact_data)
                    sector_impact_df.to_excel(writer, sheet_name='Sector Impact', index=False)
                    
                    # Create a pivot table for sector analysis
                    pivot_data = []
                    for sector in sectors:
                        sector_stocks = [s for s in results.stocks if (s.sector or "Unknown") == sector]
                        pos = len([s for s in sector_stocks if s.impact == "Positive"])
                        neg = len([s for s in sector_stocks if s.impact == "Negative"])
                        neu = len([s for s in sector_stocks if s.impact == "Neutral"])
                        total = len(sector_stocks)
                        
                        pivot_data.append({
                            "Sector": sector,
                            "Positive": pos,
                            "Negative": neg,
                            "Neutral": neu,
                            "Total": total,
                            "Positive %": (pos/total*100) if total > 0 else 0,
                            "Negative %": (neg/total*100) if total > 0 else 0,
                            "Neutral %": (neu/total*100) if total > 0 else 0
                        })
                    
                    pd.DataFrame(pivot_data).to_excel(writer, sheet_name='Sector Analysis', index=False)
                
                # Stocks analysis sheet
                stocks_data = []
                for stock in results.stocks:
                    stocks_data.append({
                        "Company": stock.stock,
                        "Ticker": stock.ticker,
                        "Sector": stock.sector or "Unknown",
                        "Impact": stock.impact,
                        "News Summary": stock.news_summary
                    })
                pd.DataFrame(stocks_data).to_excel(writer, sheet_name='Stock Analysis', index=False)
                
                # Portfolio valuation if price data is available
                valuation_data = []
                total_value = 0
                total_cost = 0
                
                for stock in results.stocks:
                    if hasattr(stock, 'quantity') and stock.quantity and hasattr(stock, 'current_price') and stock.current_price:
                        current_value = stock.quantity * stock.current_price
                        cost_value = stock.quantity * (stock.average_price or 0)
                        profit_loss = current_value - cost_value if stock.average_price else 0
                        profit_loss_pct = (profit_loss / cost_value * 100) if cost_value > 0 else 0
                        
                        valuation_data.append({
                            "Company": stock.stock,
                            "Ticker": stock.ticker,
                            "Quantity": stock.quantity,
                            "Average Price": stock.average_price,
                            "Current Price": stock.current_price,
                            "Current Value": current_value,
                            "Cost Value": cost_value,
                            "Profit/Loss": profit_loss,
                            "Profit/Loss %": profit_loss_pct
                        })
                        
                        total_value += current_value
                        total_cost += cost_value
                
                if valuation_data:
                    valuation_df = pd.DataFrame(valuation_data)
                    valuation_df.to_excel(writer, sheet_name='Portfolio Valuation', index=False)
                    
                    # Add summary row
                    summary_row = pd.DataFrame({
                        "Company": ["TOTAL"],
                        "Ticker": [""],
                        "Quantity": [""],
                        "Average Price": [""],
                        "Current Price": [""],
                        "Current Value": [total_value],
                        "Cost Value": [total_cost],
                        "Profit/Loss": [total_value - total_cost],
                        "Profit/Loss %": [(total_value - total_cost) / total_cost * 100 if total_cost > 0 else 0]
                    })
                    
                    # Write the summary row to a separate sheet
                    summary_row.to_excel(writer, sheet_name='Portfolio Summary', index=False)
                
                # Additional news sheet
                all_news = []
                for stock in results.stocks:
                    for news in stock.additional_news:
                        all_news.append({
                            "Company": stock.stock,
                            "Title": news.title,
                            "Description": news.description,
                            "Source": news.source,
                            "Published At": news.published_at,
                            "URL": news.url
                        })
                if all_news:
                    pd.DataFrame(all_news).to_excel(writer, sheet_name='Additional News', index=False)
        
        print(f"Analysis complete! Results saved to {output_file}")
        return output_file
    
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return None

def main():
    """Main function to run the Excel analyzer"""
    parser = argparse.ArgumentParser(description='Analyze portfolio or mutual fund Excel files')
    parser.add_argument('input_file', help='Path to the input Excel file')
    parser.add_argument('--output', '-o', help='Path to the output Excel file')
    parser.add_argument('--type', '-t', choices=['portfolio', 'mutual_fund', 'auto'], 
                        default='auto', help='Type of analysis to perform')
    parser.add_argument('--api-key', '-k', help='NewsAPI key for news analysis')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}")
        return 1
    
    # Run the analysis
    output_file = analyze_excel_file(
        args.input_file, 
        args.output, 
        args.type, 
        args.api_key
    )
    
    if output_file:
        print(f"Excel analysis file created: {output_file}")
        return 0
    else:
        print("Analysis failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 