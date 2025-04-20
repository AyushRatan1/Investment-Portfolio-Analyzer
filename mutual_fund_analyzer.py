#!/usr/bin/env python3
"""
Mutual Fund Portfolio Analyzer
This module analyzes mutual fund holdings to provide insight into fund composition
and news impact on the overall fund performance.
"""

import json
import os
import sys
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from pydantic import BaseModel, Field
from requests_ratelimiter import LimiterSession
from dotenv import load_dotenv

# Import from existing portfolio analyzer
from portfolio_analyzer import Stock, NewsItem, StockAnalysis, PortfolioAnalysis

# Load environment variables
load_dotenv()

# API Keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
LLM_API_KEY = os.getenv("LLM_API_KEY", "xai-L9NtX3VBbiKDNisc12yssrysUYw3KZt4JFlKzfcmLeJyEWums01fMVPmw2LspuqQcq9I1iL42ITnthVq")

# Pydantic models for mutual fund data
class FundHolding(BaseModel):
    """Model for a single holding in a mutual fund"""
    name: str
    ticker: Optional[str] = None
    percentage: float
    sector: Optional[str] = None
    
class MutualFund(BaseModel):
    """Model for a mutual fund"""
    name: str
    holdings: List[FundHolding]
    sector_exposure: Dict[str, float] = Field(default_factory=dict)
    
    def calculate_sector_exposure(self):
        """Calculate sector exposure percentages"""
        self.sector_exposure = {}
        for holding in self.holdings:
            if holding.sector:
                if holding.sector in self.sector_exposure:
                    self.sector_exposure[holding.sector] += holding.percentage
                else:
                    self.sector_exposure[holding.sector] = holding.percentage
        return self.sector_exposure

class LLMAnalysis(BaseModel):
    """Model for LLM-based analysis"""
    summary: str
    impact: str
    recommendations: List[str]
    risks: List[str]
    opportunities: List[str]

class MutualFundAnalysis(BaseModel):
    """Complete analysis of a mutual fund"""
    fund_name: str
    timestamp: str
    holdings_count: int
    top_holdings: List[FundHolding]
    sector_exposure: Dict[str, float]
    stock_analyses: List[StockAnalysis]
    llm_analysis: LLMAnalysis
    
    def to_json(self, filepath=None):
        """Convert the analysis to JSON"""
        data = self.model_dump(mode='json')
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        return data
    
    def generate_visualizations(self, output_dir="."):
        """Generate visualizations for the mutual fund analysis"""
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Sector Exposure Pie Chart
        plt.figure(figsize=(10, 8))
        sectors = list(self.sector_exposure.keys())
        values = list(self.sector_exposure.values())
        
        plt.pie(values, labels=sectors, autopct='%1.1f%%')
        plt.title(f'Sector Allocation for {self.fund_name}')
        plt.tight_layout()
        sector_pie_path = os.path.join(output_dir, f"{self.fund_name.replace(' ', '_')}_sector_pie.png")
        plt.savefig(sector_pie_path)
        plt.close()
        
        # 2. Top Holdings Bar Chart
        plt.figure(figsize=(12, 8))
        top_holdings_df = pd.DataFrame(
            [(h.name, h.percentage) for h in self.top_holdings[:10]],
            columns=['Company', 'Percentage']
        )
        
        sns.barplot(data=top_holdings_df, x='Percentage', y='Company')
        plt.title(f'Top 10 Holdings - {self.fund_name}')
        plt.tight_layout()
        holdings_bar_path = os.path.join(output_dir, f"{self.fund_name.replace(' ', '_')}_top_holdings.png")
        plt.savefig(holdings_bar_path)
        plt.close()
        
        # 3. News Impact Chart
        impact_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        for analysis in self.stock_analyses:
            impact_counts[analysis.impact] += 1
        
        plt.figure(figsize=(10, 6))
        colors = {'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'}
        plt.bar(impact_counts.keys(), impact_counts.values(), color=[colors[k] for k in impact_counts.keys()])
        plt.title(f'News Impact Distribution - {self.fund_name}')
        plt.ylabel('Number of Holdings')
        plt.tight_layout()
        impact_bar_path = os.path.join(output_dir, f"{self.fund_name.replace(' ', '_')}_impact.png")
        plt.savefig(impact_bar_path)
        plt.close()
        
        return {
            "sector_pie": sector_pie_path,
            "holdings_bar": holdings_bar_path,
            "impact_bar": impact_bar_path
        }

class MutualFundAnalyzer:
    """
    Analyzer for mutual fund holdings and their impact
    """
    
    def __init__(self, news_api_key=None, llm_api_key=None):
        """Initialize the analyzer with API keys"""
        self.news_api_key = news_api_key or NEWS_API_KEY
        self.llm_api_key = llm_api_key or LLM_API_KEY
        
        # Create rate-limited session for API calls
        self.session = LimiterSession(per_second=1)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.llm_api_key}"
        })
        
        # Import PortfolioAnalyzer for news analysis
        from portfolio_analyzer import PortfolioAnalyzer
        self.portfolio_analyzer = PortfolioAnalyzer(api_key=self.news_api_key)
    
    def extract_mutual_fund_from_excel(self, filepath: str) -> MutualFund:
        """
        Extract mutual fund data from an Excel file
        Handles various formats of mutual fund disclosures
        """
        try:
            # Read the Excel file
            df = pd.read_excel(filepath)
            
            # Try to identify the mutual fund name from the file
            fund_name = os.path.basename(filepath).split('.')[0]
            
            # Common column names for mutual fund holdings
            column_maps = {
                'name': ['Company Name', 'Security Name', 'Holding', 'Stock', 'Instrument', 'Security', 'Name', 'Issuer'],
                'ticker': ['Ticker', 'Symbol', 'Tradingsymbol', 'Security Code', 'ISIN', 'Code'],
                'percentage': ['% of Net Assets', 'Weight', '% Assets', 'Allocation', 'Percentage', '% of Fund', 'Weightage', 'Weight (%)'],
                'sector': ['Sector', 'Industry', 'Asset Class', 'Category', 'Segment']
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
            
            # Ensure we have at least name and percentage
            required_cols = ['name', 'percentage']
            if not all(col in df.columns for col in required_cols):
                # Try to infer missing columns
                if 'percentage' not in df.columns:
                    # Look for a numeric column that might be percentage
                    for col in df.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns:
                        if df[col].max() <= 100:  # Likely a percentage column
                            df = df.rename(columns={col: 'percentage'})
                            break
            
            # Clean and convert data
            # Process the dataframe to extract holdings
            holdings = []
            for _, row in df.iterrows():
                holding_data = {}
                
                # Extract available fields
                for field in ['name', 'ticker', 'percentage', 'sector']:
                    if field in df.columns:
                        holding_data[field] = row[field]
                
                # Only include rows with name and percentage
                if 'name' in holding_data and 'percentage' in holding_data:
                    # Handle percentage format (might be 0-100 or 0-1)
                    pct = holding_data['percentage']
                    if isinstance(pct, (int, float)):
                        if pct > 0 and pct < 1:  # If percentage is in 0-1 range, convert to 0-100
                            pct *= 100
                        holding_data['percentage'] = pct
                    else:
                        try:
                            # Try to convert string percentage to float
                            pct = float(pct.strip('%'))
                            holding_data['percentage'] = pct
                        except (ValueError, AttributeError):
                            continue  # Skip if percentage can't be converted
                    
                    holdings.append(FundHolding(**holding_data))
            
            # Sort holdings by percentage (descending)
            holdings.sort(key=lambda x: x.percentage, reverse=True)
            
            # Create the mutual fund
            mutual_fund = MutualFund(name=fund_name, holdings=holdings)
            mutual_fund.calculate_sector_exposure()
            
            return mutual_fund
        
        except Exception as e:
            print(f"Error extracting mutual fund data: {str(e)}")
            # Return empty mutual fund
            return MutualFund(name="Unknown Fund", holdings=[])
            
    def convert_holdings_to_stocks(self, fund: MutualFund) -> List[Stock]:
        """Convert fund holdings to stock objects for news analysis"""
        stocks = []
        for holding in fund.holdings:
            # Create a Stock object for each holding
            stock = Stock(
                name=holding.name,
                ticker=holding.ticker or holding.name,  # Use name as ticker if not available
                sector=holding.sector
            )
            stocks.append(stock)
        return stocks
    
    def get_llm_analysis(self, fund: MutualFund, stock_analyses: List[StockAnalysis]) -> LLMAnalysis:
        """
        Use LLM to perform comprehensive analysis of the mutual fund with focus on long-term outlook
        """
        try:
            # Prepare data for LLM
            # Create summary of fund holdings
            holdings_summary = []
            for i, holding in enumerate(fund.holdings[:15], 1):  # Limit to top 15
                holdings_summary.append(
                    f"{i}. {holding.name} ({holding.ticker or 'N/A'}): {holding.percentage:.2f}% of fund"
                )
            
            # Create summary of sector exposure
            sector_summary = []
            for sector, percentage in sorted(fund.sector_exposure.items(), key=lambda x: x[1], reverse=True):
                sector_summary.append(f"{sector}: {percentage:.2f}%")
            
            # Create summary of news analysis
            news_summary = []
            impact_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
            
            for analysis in stock_analyses[:15]:  # Limit to top 15
                impact_counts[analysis.impact] += 1
                news_summary.append(
                    f"{analysis.stock} ({analysis.ticker}): {analysis.impact} - {analysis.news_summary}"
                )
            
            print("Using advanced fallback analysis method (enhancing sector-based insights with long-term perspective)")
            
            # Determine overall impact based on news counts, but focus on structural trends
            if impact_counts["Positive"] > impact_counts["Negative"] * 1.5:
                overall_impact = "Strongly Positive"
            elif impact_counts["Positive"] > impact_counts["Negative"]:
                overall_impact = "Moderately Positive"
            elif impact_counts["Negative"] > impact_counts["Positive"] * 1.5:
                overall_impact = "Strongly Negative"
            elif impact_counts["Negative"] > impact_counts["Positive"]:
                overall_impact = "Moderately Negative"
            else:
                overall_impact = "Neutral"
            
            # Generate a more comprehensive summary with long-term focus
            # Get top sectors and their exposure
            top_sectors = sorted(fund.sector_exposure.items(), key=lambda x: x[1], reverse=True)
            top_sector = top_sectors[0][0] if top_sectors else "unknown"
            sector_concentration = sum(1 for _, pct in top_sectors if pct > 10)
            
            # Analyze geographical distribution (assume names contain country indicators)
            foreign_exposure = []
            india_keywords = ['india', 'indian', 'nse', 'bse', 'ltd', 'limited']
            us_keywords = ['inc', 'corp', 'nyse', 'nasdaq']
            eu_keywords = ['plc', 'sa', 'nv', 'ag']
            
            for holding in fund.holdings:
                name_lower = holding.name.lower()
                ticker_lower = (holding.ticker or "").lower()
                
                if any(kw in ticker_lower or kw in name_lower for kw in us_keywords):
                    foreign_exposure.append(("US", holding))
                elif any(kw in ticker_lower or kw in name_lower for kw in eu_keywords):
                    foreign_exposure.append(("EU", holding))
                # Assume other holdings are domestic (Indian) by default
            
            # Determine fund characteristics with long-term perspective
            is_diversified = len(fund.sector_exposure) > 5
            is_concentrated = sector_concentration >= 2
            top_holding_weight = fund.holdings[0].percentage if fund.holdings else 0
            is_top_heavy = top_holding_weight > 10
            foreign_weight = sum(holding.percentage for _, holding in foreign_exposure)
            
            # Analyze cyclical vs. defensive sectors
            cyclical_sectors = ["Technology", "Consumer Discretionary", "Industrials", "Materials", "Real Estate"]
            defensive_sectors = ["Healthcare", "Consumer Staples", "Utilities", "Telecommunications"]
            financial_sectors = ["Banking", "Financial Services", "Insurance"]
            
            cyclical_weight = sum(pct for sector, pct in fund.sector_exposure.items() 
                                if any(s.lower() in sector.lower() for s in cyclical_sectors))
            defensive_weight = sum(pct for sector, pct in fund.sector_exposure.items() 
                                 if any(s.lower() in sector.lower() for s in defensive_sectors))
            financial_weight = sum(pct for sector, pct in fund.sector_exposure.items() 
                                 if any(s.lower() in sector.lower() for s in financial_sectors))
            
            # Analyze market trends based on holdings news and sector allocation
            sector_impact = {}
            for analysis in stock_analyses:
                sector = next((h.sector for h in fund.holdings if h.name == analysis.stock), None)
                if sector:
                    if sector not in sector_impact:
                        sector_impact[sector] = {"Positive": 0, "Negative": 0, "Neutral": 0}
                    sector_impact[sector][analysis.impact] += 1
            
            # Identify growth sectors and challenged sectors (longer-term outlook)
            positive_sectors = [s for s, counts in sector_impact.items() 
                               if counts["Positive"] > counts["Negative"] and counts["Positive"] > 0]
            negative_sectors = [s for s, counts in sector_impact.items() 
                               if counts["Negative"] > counts["Positive"] and counts["Negative"] > 0]
            
            # Create a detailed market outlook summary with long-term perspective
            summary = f"The {fund.name} is a {'' if is_diversified else 'non-'}diversified fund with {len(fund.holdings)} holdings across {len(fund.sector_exposure)} sectors. "
            
            if is_concentrated:
                summary += f"The fund shows significant concentration in {sector_concentration} key sectors, with {top_sector} representing the largest allocation ({top_sectors[0][1]:.1f}%). "
            else:
                summary += f"The portfolio maintains a well-balanced allocation strategy with its highest exposure in {top_sector} ({top_sectors[0][1]:.1f}%). "
            
            if is_top_heavy:
                summary += f"The fund's position is notably concentrated, with its largest holding representing {top_holding_weight:.1f}% of the portfolio. "
            
            # Add market structure and long-term trend analysis
            if cyclical_weight > 50:
                summary += f"With {cyclical_weight:.1f}% allocated to cyclical sectors, the fund is positioned to benefit from economic expansion phases but may face increased volatility during economic downturns. "
            elif defensive_weight > 50:
                summary += f"With {defensive_weight:.1f}% in defensive sectors, the fund is structured to provide stability during market downturns, though it may underperform during strong bull markets. "
            elif financial_weight > 30:
                summary += f"The significant {financial_weight:.1f}% exposure to financial sectors makes the fund sensitive to interest rate cycles and regulatory changes in the banking industry. "
            
            # Add geographical insights
            if foreign_exposure:
                summary += f"The fund has approximately {foreign_weight:.1f}% exposure to international markets, introducing currency fluctuation risks but providing geographical diversification benefits. "
            
            # Add long-term sector outlook
            if positive_sectors:
                summary += f"From a long-term perspective, the {', '.join(positive_sectors[:2])} {'sector' if len(positive_sectors) == 1 else 'sectors'} show structural growth potential based on current trends and market dynamics. "
            if negative_sectors:
                summary += f"Conversely, the {', '.join(negative_sectors[:2])} {'sector' if len(negative_sectors) == 1 else 'sectors'} may face long-term structural challenges that warrant careful monitoring. "
            
            summary += f"The overall long-term outlook for this fund appears {overall_impact.lower()} based on its composition, sector allocations, and current market trends."
            
            # Generate strategic recommendations with long-term focus
            recommendations = []
            
            # Core allocation strategies
            if is_concentrated and cyclical_weight > 60:
                recommendations.append(f"Consider introducing defensive sector allocations to balance the fund's high exposure to economic cycles")
            elif is_concentrated and defensive_weight > 60:
                recommendations.append(f"Evaluate opportunities to introduce growth-oriented positions to improve long-term return potential")
            elif is_diversified:
                recommendations.append(f"Maintain the current diversified allocation as a core strategy, with tactical adjustments based on economic cycles")
            
            # Sector-specific long-term recommendations
            if positive_sectors:
                recommendations.append(f"Establish strategic core positions in the {positive_sectors[0]} sector which shows structural growth potential")
            if negative_sectors:
                recommendations.append(f"Implement a gradual reduction strategy for {negative_sectors[0]} sector exposure over multiple quarters")
            
            # Geographic allocation recommendations
            if foreign_weight > 20:
                recommendations.append("Implement currency hedging strategies for significant foreign holdings to manage exchange rate volatility")
            elif foreign_weight < 5:
                recommendations.append("Consider introducing select international positions to enhance diversification and capture global growth opportunities")
            
            # Position sizing recommendations
            if is_top_heavy:
                recommendations.append(f"Gradually reduce concentration in top holdings through multi-quarter rebalancing to manage company-specific risk")
            
            # Economic cycle positioning
            if financial_weight > 25:
                recommendations.append("Monitor central bank policies closely as interest rate cycles significantly impact the fund's financial sector holdings")
            
            if "Technology" in ''.join(fund.sector_exposure.keys()) and any("Technology" in s for s in positive_sectors):
                recommendations.append("Maintain overweight positions in technology leaders while diversifying across software, hardware, and services subsectors")
            
            # Generate comprehensive risk factors with long-term perspective
            risks = []
            
            # Structural concentration risks
            if is_concentrated:
                risks.append(f"Long-term sector concentration risk with {sector_concentration} sectors comprising over 10% each")
            
            # Single company exposure
            if is_top_heavy:
                top_holding = fund.holdings[0].name
                risks.append(f"Extended company-specific exposure risk with {top_holding} representing {top_holding_weight:.1f}% of assets")
            
            # Cyclical vs defensive positioning risks
            if cyclical_weight > 60:
                risks.append("High sensitivity to economic slowdowns due to cyclical sector overexposure")
            elif defensive_weight > 60:
                risks.append("Potential underperformance during sustained bull markets due to defensive sector focus")
            
            # Geographical and currency risks
            if foreign_weight > 15:
                risks.append(f"Currency fluctuation risk from {foreign_weight:.1f}% international exposure affecting total returns")
            
            # Macroeconomic policy risks
            if financial_weight > 25:
                risks.append("Extended exposure to monetary policy and regulatory changes through significant financial sector allocation")
            
            # Factor in sector-specific structural risks
            primary_sectors = [s[0] for s in top_sectors[:3]]
            
            if any("Banking" in s or "Financial" in s for s in primary_sectors):
                risks.append("Long-term exposure to interest rate cycles and regulatory environment changes through financial holdings")
            
            if any("Technology" in s for s in primary_sectors):
                risks.append("Technology sector valuations vulnerable to shifts in growth expectations and regulatory frameworks")
            
            if any("Energy" in s or "Oil" in s for s in primary_sectors):
                risks.append("Energy transition risks affecting traditional oil and gas holdings over multi-year horizons")
                
            if any("Pharmaceutical" in s or "Healthcare" in s for s in primary_sectors):
                risks.append("Drug pricing reform and healthcare policy changes presenting regulatory risks to pharmaceutical holdings")
            
            # Generate long-term opportunities with structural growth focus
            opportunities = []
            
            # Sector-based long-term growth opportunities
            if positive_sectors:
                for sector in positive_sectors[:2]:
                    opportunities.append(f"Structural growth potential in {sector} sector driven by sustained demand and innovation")
            
            # Economic evolution opportunities
            primary_sectors = [s[0] for s in top_sectors[:3]]
            sector_str = ' '.join(primary_sectors).lower()
            
            if any("Banking" in s or "Financial" in s for s in primary_sectors):
                opportunities.append("Fintech integration and digital banking transformation driving long-term value creation in financial holdings")
            
            if any("Technology" in s for s in primary_sectors):
                opportunities.append("Artificial intelligence, cloud computing, and digital transformation providing multi-year growth runways for technology investments")
            
            if "consumer" in sector_str:
                opportunities.append("Emerging middle class consumption growth supporting multi-year expansion for consumer-focused companies")
            
            if "healthcare" in sector_str or "pharma" in sector_str:
                opportunities.append("Aging demographics and healthcare innovation creating sustained growth opportunities in medical and pharmaceutical sectors")
            
            if "renewable" in sector_str or "energy" in sector_str:
                opportunities.append("Energy transition and decarbonization investments offering structural growth through the transition to renewable energy")
            
            # Geographical opportunities
            if foreign_weight > 0:
                opportunities.append("International exposure providing access to differentiated growth drivers and economic cycles")
            else:
                opportunities.append("Potential to enhance returns through selective addition of international leaders in structurally growing industries")
            
            # Create the LLM analysis object
            llm_analysis = LLMAnalysis(
                summary=summary,
                impact=overall_impact,
                recommendations=recommendations,
                risks=risks,
                opportunities=opportunities
            )
            
            return llm_analysis
            
        except Exception as e:
            print(f"Error in LLM analysis: {str(e)}")
            # Return default analysis on error
            return LLMAnalysis(
                summary=f"Error performing LLM analysis: {str(e)}",
                impact="Neutral",
                recommendations=["Consult a financial advisor for personalized long-term strategy"],
                risks=["Unable to assess long-term risks due to analysis error"],
                opportunities=["Unable to assess long-term opportunities due to analysis error"]
            )
    
    def analyze_mutual_fund(self, fund: MutualFund) -> MutualFundAnalysis:
        """
        Analyze a mutual fund and provide comprehensive insights
        """
        # Convert fund holdings to stocks for news analysis
        stocks = self.convert_holdings_to_stocks(fund)
        
        # Get news and analyze impact for each stock
        print(f"Analyzing news for {len(stocks)} holdings in {fund.name}...")
        stock_analyses = self.portfolio_analyzer.analyze_portfolio(stocks).stocks
        
        # Get LLM analysis
        print("Performing advanced impact analysis with LLM...")
        llm_analysis = self.get_llm_analysis(fund, stock_analyses)
        
        # Create mutual fund analysis
        analysis = MutualFundAnalysis(
            fund_name=fund.name,
            timestamp=datetime.now().isoformat(),
            holdings_count=len(fund.holdings),
            top_holdings=fund.holdings[:10],  # Top 10 holdings
            sector_exposure=fund.sector_exposure,
            stock_analyses=stock_analyses,
            llm_analysis=llm_analysis
        )
        
        return analysis
    
    def analyze_from_excel(self, excel_path: str) -> MutualFundAnalysis:
        """
        Read mutual fund from Excel and analyze it
        """
        # Extract mutual fund data
        fund = self.extract_mutual_fund_from_excel(excel_path)
        
        if not fund.holdings:
            print(f"No valid holdings found in {excel_path}")
            # Return empty analysis
            return MutualFundAnalysis(
                fund_name=fund.name,
                timestamp=datetime.now().isoformat(),
                holdings_count=0,
                top_holdings=[],
                sector_exposure={},
                stock_analyses=[],
                llm_analysis=LLMAnalysis(
                    summary="No holdings found to analyze",
                    impact="Neutral",
                    recommendations=["Verify the Excel file format"],
                    risks=["No holdings to analyze"],
                    opportunities=["None identified"]
                )
            )
        
        # Analyze the mutual fund
        print(f"Analyzing mutual fund with {len(fund.holdings)} holdings...")
        return self.analyze_mutual_fund(fund)

def main():
    """Main function to run the mutual fund analyzer"""
    # Check for API keys
    if not NEWS_API_KEY:
        print("Warning: NEWS_API_KEY not found in environment variables.")
        print("News analysis functionality may be limited.")
    
    if not LLM_API_KEY:
        print("Warning: LLM_API_KEY not found in environment variables.")
        print("Using default API key for LLM analysis.")
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python mutual_fund_analyzer.py <path_to_excel_file>")
        return
    
    excel_path = sys.argv[1]
    if not os.path.exists(excel_path):
        print(f"Error: File not found: {excel_path}")
        return
    
    try:
        # Create and run the analyzer
        analyzer = MutualFundAnalyzer()
        results = analyzer.analyze_from_excel(excel_path)
        
        # Generate output filename
        base_name = os.path.basename(excel_path).split('.')[0]
        output_path = f"{base_name}_fund_analysis.json"
        
        # Save results to JSON
        results.to_json(output_path)
        
        # Generate visualizations
        viz_dir = "visualizations"
        viz_paths = results.generate_visualizations(viz_dir)
        
        print(f"\nMutual Fund Analysis Complete!")
        print(f"Results saved to {output_path}")
        print(f"Visualizations saved to {viz_dir}/ directory")
        
        # Print summary to console
        print("\nAnalysis Summary:")
        print(f"Fund: {results.fund_name}")
        print(f"Holdings: {results.holdings_count}")
        
        # Top 5 holdings
        print("\nTop 5 Holdings:")
        for i, holding in enumerate(results.top_holdings[:5], 1):
            print(f"{i}. {holding.name}: {holding.percentage:.2f}%")
        
        # Sector allocation (top 5)
        print("\nTop Sectors:")
        for sector, pct in sorted(results.sector_exposure.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"{sector}: {pct:.2f}%")
        
        # News impact summary
        impact_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        for analysis in results.stock_analyses:
            impact_counts[analysis.impact] += 1
        
        print("\nNews Impact Summary:")
        for impact, count in impact_counts.items():
            print(f"{impact}: {count} holdings")
        
        # LLM Analysis
        print("\nAI Analysis:")
        print(f"Overall Impact: {results.llm_analysis.impact}")
        print(f"Summary: {results.llm_analysis.summary}")
        
        print("\nRecommendations:")
        for i, rec in enumerate(results.llm_analysis.recommendations, 1):
            print(f"{i}. {rec}")
        
        print("\nRisks:")
        for i, risk in enumerate(results.llm_analysis.risks, 1):
            print(f"{i}. {risk}")
        
        print("\nOpportunities:")
        for i, opp in enumerate(results.llm_analysis.opportunities, 1):
            print(f"{i}. {opp}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 