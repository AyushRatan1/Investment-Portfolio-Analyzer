#!/usr/bin/env python3
"""
Portfolio Analyzer Web Application
A Streamlit-based frontend for the Investment Portfolio Analysis AI Agent
"""

import os
import streamlit as st
import pandas as pd
import json
import base64
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt

# Import analyzers
from mutual_fund_analyzer import MutualFundAnalyzer
from portfolio_analyzer import PortfolioAnalyzer

# Set page config
st.set_page_config(
    page_title="Investment Portfolio Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a more professional look
st.markdown("""
<style>
    .main {
        background-color: #f9f9f9;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .title-container {
        background-color: #0e1117;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .metric-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin: 10px;
        min-width: 200px;
        text-align: center;
    }
    .positive {
        color: #28a745;
    }
    .negative {
        color: #dc3545;
    }
    .neutral {
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

def get_binary_file_downloader_html(bin_file, file_label='File'):
    """Generate HTML code for a download link for binary file"""
    with open(bin_file, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href

def results_to_excel(results, analysis_type="portfolio"):
    """Convert analysis results to Excel file and return the file path"""
    # Create output directory if it doesn't exist
    os.makedirs("downloads", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"downloads/{analysis_type}_analysis_{timestamp}.xlsx"
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        if analysis_type == "mutual_fund":
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
            # Summary sheet
            summary_data = {
                "Analysis Date": [results.timestamp],
                "Stocks Count": [len(results.stocks)]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Stocks analysis sheet
            stocks_data = []
            for stock in results.stocks:
                stocks_data.append({
                    "Company": stock.stock,
                    "Ticker": stock.ticker,
                    "Impact": stock.impact,
                    "News Summary": stock.news_summary
                })
            pd.DataFrame(stocks_data).to_excel(writer, sheet_name='Stock Analysis', index=False)
            
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

    return output_path

def display_portfolio_results(results):
    """Display portfolio analysis results in a user-friendly way"""
    # Convert to normal Python dict if it's a Pydantic model
    if hasattr(results, 'model_dump'):
        results_dict = results.model_dump()
    else:
        results_dict = results
    
    # Group stocks by impact
    positive_stocks = []
    negative_stocks = []
    neutral_stocks = []
    
    for stock in results.stocks:
        if stock.impact == "Positive":
            positive_stocks.append(stock)
        elif stock.impact == "Negative":
            negative_stocks.append(stock)
        else:
            neutral_stocks.append(stock)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Positive Impact", len(positive_stocks))
    with col2:
        st.metric("Neutral Impact", len(neutral_stocks))
    with col3:
        st.metric("Negative Impact", len(negative_stocks))
    
    # Check if we have price data available
    has_price_data = any(
        hasattr(stock, 'current_price') and stock.current_price is not None 
        for stock in results.stocks
    )
    
    # Create tabs for different views
    if has_price_data:
        tab1, tab2, tab3 = st.tabs(["Stock Impact", "All News", "Portfolio Valuation"])
    else:
        tab1, tab2 = st.tabs(["Stock Impact", "All News"])
    
    with tab1:
        # Display stocks grouped by impact
        st.subheader("📈 Positive Impact Stocks")
        if positive_stocks:
            for stock in positive_stocks:
                with st.expander(f"{stock.stock} ({stock.ticker})"):
                    st.markdown(f"**News Summary:** {stock.news_summary}")
                    if stock.additional_news:
                        st.markdown("**Additional Headlines:**")
                        for news in stock.additional_news:
                            st.markdown(f"- {news.title}")
                    
                    # Add fallback message if news is from system
                    if (not stock.additional_news and 
                        "No significant news found" in stock.news_summary):
                        st.info("ℹ️ Try adding a NewsAPI key in the sidebar to get real news updates.")
        else:
            st.info("No stocks with positive impact found")
        
        st.subheader("📉 Negative Impact Stocks")
        if negative_stocks:
            for stock in negative_stocks:
                with st.expander(f"{stock.stock} ({stock.ticker})"):
                    st.markdown(f"**News Summary:** {stock.news_summary}")
                    if stock.additional_news:
                        st.markdown("**Additional Headlines:**")
                        for news in stock.additional_news:
                            st.markdown(f"- {news.title}")
                    
                    # Add fallback message if news is from system
                    if (not stock.additional_news and 
                        "No significant news found" in stock.news_summary):
                        st.info("ℹ️ Try adding a NewsAPI key in the sidebar to get real news updates.")
        else:
            st.info("No stocks with negative impact found")
        
        st.subheader("📊 Neutral Impact Stocks")
        if neutral_stocks:
            for stock in neutral_stocks:
                with st.expander(f"{stock.stock} ({stock.ticker})"):
                    st.markdown(f"**News Summary:** {stock.news_summary}")
                    if stock.additional_news:
                        st.markdown("**Additional Headlines:**")
                        for news in stock.additional_news:
                            st.markdown(f"- {news.title}")
                    
                    # Add fallback message if news is from system
                    if (not stock.additional_news and 
                        "No significant news found" in stock.news_summary):
                        st.info("ℹ️ Try adding a NewsAPI key in the sidebar to get real news updates.")
        else:
            st.info("No stocks with neutral impact found")
    
    with tab2:
        # Display all news in a table
        news_data = []
        for stock in results.stocks:
            news_data.append({
                "Company": stock.stock,
                "Ticker": stock.ticker,
                "Sector": getattr(stock, 'sector', 'Unknown'),
                "Impact": stock.impact,
                "News": stock.news_summary
            })
        
        df = pd.DataFrame(news_data)
        st.dataframe(df, use_container_width=True)
        
        # Display a warning if all news items are "No significant news found"
        if all("No significant news found" in item["News"] for item in news_data):
            st.warning("""
                ⚠️ No news was found for any stocks in your portfolio. 
                To get real news data, please add a NewsAPI key in the sidebar.
                You can get a free key at [NewsAPI.org](https://newsapi.org/register).
            """)
    
    # Add portfolio valuation tab if price data is available
    if has_price_data and 'tab3' in locals():
        with tab3:
            st.subheader("Portfolio Valuation")
            
            valuation_data = []
            total_value = 0
            total_cost = 0
            
            for stock in results.stocks:
                if (hasattr(stock, 'quantity') and stock.quantity and 
                    hasattr(stock, 'current_price') and stock.current_price):
                    current_value = stock.quantity * stock.current_price
                    cost_value = stock.quantity * (stock.average_price or 0)
                    profit_loss = current_value - cost_value if stock.average_price else 0
                    profit_loss_pct = (profit_loss / cost_value * 100) if cost_value > 0 else 0
                    
                    valuation_data.append({
                        "Company": stock.stock,
                        "Ticker": stock.ticker,
                        "Quantity": stock.quantity,
                        "Average Price": f"{stock.average_price:.2f}" if stock.average_price else "N/A",
                        "Current Price": f"{stock.current_price:.2f}",
                        "Current Value": f"{current_value:.2f}",
                        "Cost Value": f"{cost_value:.2f}" if stock.average_price else "N/A",
                        "Profit/Loss": f"{profit_loss:.2f}" if stock.average_price else "N/A",
                        "Profit/Loss %": f"{profit_loss_pct:.2f}%" if stock.average_price else "N/A"
                    })
                    
                    total_value += current_value
                    total_cost += cost_value
            
            if valuation_data:
                # Add total row
                valuation_data.append({
                    "Company": "TOTAL",
                    "Ticker": "",
                    "Quantity": "",
                    "Average Price": "",
                    "Current Price": "",
                    "Current Value": f"{total_value:.2f}",
                    "Cost Value": f"{total_cost:.2f}",
                    "Profit/Loss": f"{total_value - total_cost:.2f}",
                    "Profit/Loss %": f"{(total_value - total_cost) / total_cost * 100:.2f}%" if total_cost > 0 else "N/A"
                })
                
                st.table(pd.DataFrame(valuation_data))
                
                # Add a pie chart showing portfolio allocation
                st.subheader("Portfolio Allocation")
                fig_col1, fig_col2 = st.columns(2)
                
                with fig_col1:
                    # Create allocation by stock
                    stock_values = [stock.quantity * stock.current_price 
                                     for stock in results.stocks 
                                     if hasattr(stock, 'quantity') and stock.quantity and 
                                        hasattr(stock, 'current_price') and stock.current_price]
                    stock_names = [stock.stock 
                                    for stock in results.stocks 
                                    if hasattr(stock, 'quantity') and stock.quantity and 
                                       hasattr(stock, 'current_price') and stock.current_price]
                    
                    fig = plt.figure(figsize=(6, 6))
                    plt.pie(stock_values, labels=stock_names, autopct='%1.1f%%')
                    plt.title('Allocation by Stock')
                    st.pyplot(fig)
                
                with fig_col2:
                    # Create allocation by sector
                    sector_data = {}
                    for stock in results.stocks:
                        if (hasattr(stock, 'quantity') and stock.quantity and 
                            hasattr(stock, 'current_price') and stock.current_price):
                            sector = stock.sector or "Unknown"
                            value = stock.quantity * stock.current_price
                            if sector in sector_data:
                                sector_data[sector] += value
                            else:
                                sector_data[sector] = value
                    
                    if sector_data:
                        fig = plt.figure(figsize=(6, 6))
                        plt.pie(list(sector_data.values()), labels=list(sector_data.keys()), autopct='%1.1f%%')
                        plt.title('Allocation by Sector')
                        st.pyplot(fig)
            else:
                st.info("No price data available for portfolio valuation")
    
    # Generate Excel file for download
    excel_path = results_to_excel(results, "portfolio")
    st.markdown("### Download Results")
    st.markdown(get_binary_file_downloader_html(excel_path, 'Download Excel Report'), unsafe_allow_html=True)

def display_mutual_fund_results(results):
    """Display mutual fund analysis results in a user-friendly way"""
    st.markdown(f"## {results.fund_name} Analysis Results")
    
    # Display key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Holdings", results.holdings_count)
    with col2:
        st.metric("Impact Assessment", results.llm_analysis.impact)
    
    # Calculate impact counts
    impact_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for analysis in results.stock_analyses:
        impact_counts[analysis.impact] += 1
    
    with col3:
        if impact_counts["Positive"] > impact_counts["Negative"]:
            trend = "up"
        elif impact_counts["Negative"] > impact_counts["Positive"]:
            trend = "down"
        else:
            trend = None
        st.metric("Positive News", f"{impact_counts['Positive']}/{len(results.stock_analyses)}", delta_color="normal", delta=trend)
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Fund Composition", "News Impact", "AI Analysis", "Visualizations"])
    
    with tab1:
        # Display top holdings
        st.subheader("Top Holdings")
        holdings_data = []
        for holding in results.top_holdings[:10]:
            holdings_data.append({
                "Company": holding.name,
                "Ticker": holding.ticker or "N/A",
                "Sector": holding.sector or "N/A",
                "% of Fund": f"{holding.percentage:.2f}%"
            })
        
        st.table(pd.DataFrame(holdings_data))
        
        # Display sector allocation
        st.subheader("Sector Allocation")
        sector_data = []
        for sector, percentage in sorted(results.sector_exposure.items(), key=lambda x: x[1], reverse=True):
            sector_data.append({
                "Sector": sector,
                "Allocation": f"{percentage:.2f}%"
            })
        
        st.table(pd.DataFrame(sector_data))
    
    with tab2:
        # Display news impact
        st.subheader("News Impact Analysis")
        
        # Group by impact
        for impact in ["Positive", "Negative", "Neutral"]:
            st.markdown(f"#### {impact} Impact")
            impact_news = [a for a in results.stock_analyses if a.impact == impact]
            
            if impact_news:
                news_data = []
                for analysis in impact_news:
                    news_data.append({
                        "Company": analysis.stock,
                        "Ticker": analysis.ticker,
                        "News": analysis.news_summary
                    })
                
                st.table(pd.DataFrame(news_data))
            else:
                st.info(f"No {impact.lower()} impact news found")
    
    with tab3:
        # Display AI analysis
        st.subheader("AI Analysis")
        st.markdown(f"**Summary:** {results.llm_analysis.summary}")
        st.markdown(f"**Overall Impact:** {results.llm_analysis.impact}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Recommendations")
            for rec in results.llm_analysis.recommendations:
                st.markdown(f"- {rec}")
            
            st.markdown("#### Risks")
            for risk in results.llm_analysis.risks:
                st.markdown(f"- {risk}")
        
        with col2:
            st.markdown("#### Opportunities")
            for opp in results.llm_analysis.opportunities:
                st.markdown(f"- {opp}")
    
    with tab4:
        # Display visualizations
        st.subheader("Visualizations")
        
        # Check if visualization files exist
        viz_dir = "visualizations"
        fund_name_safe = results.fund_name.replace(' ', '_')
        
        sector_pie = os.path.join(viz_dir, f"{fund_name_safe}_sector_pie.png")
        holdings_bar = os.path.join(viz_dir, f"{fund_name_safe}_top_holdings.png")
        impact_bar = os.path.join(viz_dir, f"{fund_name_safe}_impact.png")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if os.path.exists(sector_pie):
                st.image(sector_pie, caption="Sector Allocation")
            
            if os.path.exists(impact_bar):
                st.image(impact_bar, caption="News Impact Distribution")
        
        with col2:
            if os.path.exists(holdings_bar):
                st.image(holdings_bar, caption="Top Holdings")
    
    # Generate Excel file for download
    excel_path = results_to_excel(results, "mutual_fund")
    st.markdown("### Download Results")
    st.markdown(get_binary_file_downloader_html(excel_path, 'Download Excel Report'), unsafe_allow_html=True)

def main():
    """Main function for the Streamlit app"""
    # Display app header
    st.markdown('<div class="title-container"><h1>Investment Portfolio Analyzer</h1><p>Analyze your stock portfolio and mutual funds with AI-powered insights</p></div>', unsafe_allow_html=True)
    
    # Sidebar for navigation and file upload
    st.sidebar.markdown("## Analysis Options")
    analysis_type = st.sidebar.radio("Select Analysis Type", ["Mutual Fund Analysis", "Portfolio Analysis"])
    
    # API key configuration
    with st.sidebar.expander("API Key Configuration"):
        news_api_key = st.text_input("NewsAPI Key", value=os.getenv("NEWS_API_KEY", ""))
        if news_api_key:
            os.environ["NEWS_API_KEY"] = news_api_key
            st.success("News API key set!")
        else:
            st.warning("News API key is required for full functionality")
    
    # File upload section
    st.sidebar.markdown("## Upload File")
    uploaded_file = st.sidebar.file_uploader("Choose an Excel file", type="xlsx")
    
    # Sample files option
    st.sidebar.markdown("## Sample Files")
    sample_files = []
    
    if analysis_type == "Mutual Fund Analysis":
        if os.path.exists("samples"):
            sample_files = [f for f in os.listdir("samples") if f.endswith(".xlsx") and "Fund" in f]
    else:
        if os.path.exists("samples"):
            sample_files = [f for f in os.listdir("samples") if f.endswith(".xlsx") and "portfolio" in f]
    
    selected_sample = st.sidebar.selectbox("Select a sample file", [""] + sample_files)
    
    # Main content area
    if analysis_type == "Mutual Fund Analysis":
        st.markdown('<div class="card"><h2>Mutual Fund Analysis</h2><p>Upload your mutual fund Excel file to analyze holdings, sector allocation, and news impact</p></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card"><h2>Portfolio Analysis</h2><p>Upload your stock portfolio Excel file to get news insights and impact assessment</p></div>', unsafe_allow_html=True)
    
    # Handle file analysis
    file_to_analyze = None
    
    if uploaded_file:
        # Save the uploaded file temporarily
        temp_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        file_to_analyze = temp_path
        st.success(f"File uploaded: {uploaded_file.name}")
    
    elif selected_sample:
        file_to_analyze = os.path.join("samples", selected_sample)
        st.info(f"Using sample file: {selected_sample}")
    
    # Analyze button
    if file_to_analyze:
        if st.button("Analyze", key="analyze_button", type="primary"):
            with st.spinner("Analyzing... This may take a moment."):
                try:
                    if analysis_type == "Mutual Fund Analysis":
                        # Run mutual fund analysis
                        analyzer = MutualFundAnalyzer(news_api_key=os.getenv("NEWS_API_KEY"))
                        results = analyzer.analyze_from_excel(file_to_analyze)
                        
                        # Ensure visualizations are generated
                        results.generate_visualizations("visualizations")
                        
                        # Display results
                        display_mutual_fund_results(results)
                    else:
                        # Run portfolio analysis
                        analyzer = PortfolioAnalyzer(api_key=os.getenv("NEWS_API_KEY"))
                        results = analyzer.analyze_from_excel(file_to_analyze)
                        
                        # Display results
                        display_portfolio_results(results)
                
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
    else:
        st.info("Please upload a file or select a sample file to begin analysis")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.markdown("""
    This tool analyzes your investments using AI technology to provide meaningful insights about your portfolio.
    
    - Processes Excel files from various platforms
    - Provides news analysis and impact assessment
    - Generates detailed reports in Excel format
    """)

if __name__ == "__main__":
    main() 