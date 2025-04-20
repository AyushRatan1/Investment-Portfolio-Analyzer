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

# Custom CSS for a dark-themed professional fund manager look
st.markdown("""
<style>
    /* Base styling */
    .main {
        background-color: #1e1e2e;
        color: #e0e0e0;
    }
    .stApp {
        max-width: 1300px;
        margin: 0 auto;
        background-color: #1e1e2e;
    }
    
    /* Header styling */
    .title-container {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    /* Card styling */
    .card {
        background-color: #2d2d3f;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        border-top: 4px solid #4e73df;
    }
    
    /* Dashboard metrics */
    .metric-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    .metric-card {
        background-color: #2d2d3f;
        border-radius: 10px;
        padding: 15px;
        margin: 10px;
        min-width: 200px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        border-left: 4px solid #4e73df;
    }
    
    /* Status colors */
    .positive {
        color: #4ecdc4;
    }
    .negative {
        color: #ff6b6b;
    }
    .neutral {
        color: #ffe066;
    }
    
    /* Section headers */
    .section-header {
        border-bottom: 2px solid #3f3f5a;
        padding-bottom: 10px;
        margin-bottom: 20px;
        color: #e0e0e0;
        font-size: 1.2rem;
        font-weight: 700;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-163ttbj, .css-1wrcr25 {
        background-color: #1e1e2e;
    }
    
    /* Make tabs more prominent */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2d2d3f;
        padding: 8px 16px;
        border-radius: 4px 4px 0 0;
        color: #e0e0e0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4e73df !important;
        color: white !important;
    }
    
    /* Tables */
    .dataframe {
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        font-family: sans-serif;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
        border-radius: 8px;
        overflow: hidden;
        background-color: #2d2d3f;
        color: #e0e0e0;
    }
    .dataframe thead tr {
        background-color: #4e73df;
        color: white;
        text-align: left;
    }
    .dataframe th,
    .dataframe td {
        padding: 12px 15px;
        color: #e0e0e0;
    }
    .dataframe tbody tr {
        border-bottom: thin solid #3f3f5a;
    }
    .dataframe tbody tr:nth-of-type(even) {
        background-color: #32324a;
    }
    .dataframe tbody tr:last-of-type {
        border-bottom: 2px solid #4e73df;
    }
    
    /* Fund manager note styling */
    .fund-manager-note {
        background-color: #2d2d3f;
        border-left: 4px solid #4e73df;
        padding: 15px;
        margin: 20px 0;
        border-radius: 0 8px 8px 0;
        color: #e0e0e0;
    }
    
    /* Recommendation badges */
    .badge-buy {
        background-color: #4ecdc4;
        color: #1e1e2e;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-right: 5px;
    }
    .badge-hold {
        background-color: #ffe066;
        color: #1e1e2e;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-right: 5px;
    }
    .badge-sell {
        background-color: #ff6b6b;
        color: #1e1e2e;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-right: 5px;
    }
    
    /* Strategy cards */
    .strategy-card {
        border: 1px solid #3f3f5a;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        transition: transform 0.2s, box-shadow 0.2s;
        background-color: #2d2d3f;
        color: #e0e0e0;
    }
    .strategy-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Progress bars */
    .progress-container {
        width: 100%;
        background-color: #3f3f5a;
        border-radius: 4px;
        margin: 5px 0;
    }
    .progress-bar {
        height: 8px;
        border-radius: 4px;
        text-align: center;
        line-height: 8px;
        color: white;
    }

    /* Improve visibility for all text elements */
    p, li, span, div {
        color: #e0e0e0;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #e0e0e0;
    }
    
    /* Override all Streamlit elements for dark theme */
    .stTextInput > div > div > input {
        background-color: #2d2d3f;
        color: #e0e0e0;
    }
    
    .stSelectbox > div > div > div {
        background-color: #2d2d3f;
        color: #e0e0e0;
    }
    
    .stMultiSelect > div > div > div {
        background-color: #2d2d3f;
        color: #e0e0e0;
    }
    
    .css-145kmo2 {
        color: #e0e0e0;
    }
    
    /* Fix for Streamlit components */
    .streamlit-expanderHeader, .streamlit-expanderContent {
        background-color: #2d2d3f !important;
        color: #e0e0e0 !important;
    }
    
    /* Fix for white card backgrounds */
    div.css-1r6slb0, div.css-12w0qpk, div.css-1invdo7 {
        background-color: #2d2d3f !important;
        color: #e0e0e0 !important;
    }
    
    /* Ensure text is readable against darker backgrounds */
    .css-18e3th9 {
        padding-top: 0;
        padding-bottom: 0;
        color: #e0e0e0;
    }
    
    /* Improve expander styling */
    .streamlit-expanderContent {
        border: none !important;
        border-top: 1px solid #3f3f5a !important;
    }
    
    /* Fix for Streamlit elements */
    button, .stButton>button {
        background-color: #4e73df;
        color: white;
    }
    
    button:hover, .stButton>button:hover {
        background-color: #3a5ecc;
    }
    
    .stAlert {
        background-color: #32324a;
        color: #e0e0e0;
    }
    
    .stAlert > div {
        color: #e0e0e0;
    }
    
    /* Info, success, warning boxes */
    .element-container .stAlert .st-be {
        background-color: #32324a !important;
        color: #e0e0e0 !important;
    }
    
    /* Fix for plots and charts */
    .js-plotly-plot .plotly {
        background-color: #2d2d3f !important;
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
    """Display mutual fund analysis results in a comprehensive fund manager dashboard"""
    # Create a professional header with fund name and analysis timestamp
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2 style="margin: 0;">{results.fund_name} Analysis</h2>
        <span style="color: #9e9e9e; font-size: 0.9em;">Analysis Date: {results.timestamp[:10]}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Add executive summary box
    # Determine fund type based on sector exposures
    top_sectors = sorted(results.sector_exposure.items(), key=lambda x: x[1], reverse=True)
    top_sector = top_sectors[0][0] if top_sectors else "Diversified"
    
    sector_focus = "Sector-focused" if top_sectors and top_sectors[0][1] > 30 else "Diversified"
    size_desc = "Large-cap" if "Large" in results.fund_name else ("Small-cap" if "Small" in results.fund_name else "Mixed-cap")
    
    is_tech_focused = any("Tech" in s for s, _ in top_sectors[:2])
    is_financial_focused = any(s in ["Banking", "Financial Services", "Finance"] for s, _ in top_sectors[:2])
    is_consumer_focused = any("Consumer" in s for s, _ in top_sectors[:2])
    
    if is_tech_focused:
        fund_type = f"{size_desc} Technology"
    elif is_financial_focused:
        fund_type = f"{size_desc} Financial Services"
    elif is_consumer_focused:
        fund_type = f"{size_desc} Consumer"
    else:
        fund_type = f"{size_desc} {sector_focus}"
    
    # Generate the executive summary
    if results.llm_analysis.impact in ["Strongly Positive", "Moderately Positive"]:
        recommendation = "BUY"
        rec_color = "#4ecdc4"
    elif results.llm_analysis.impact == "Neutral":
        recommendation = "HOLD"
        rec_color = "#ffe066"
    else:
        recommendation = "REDUCE"
        rec_color = "#ff6b6b"
    
    # Executive summary card
    st.markdown(f"""
    <div style="background-color: #2d2d3f; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2); margin-bottom: 30px; border-left: 5px solid {rec_color};">
        <h3 style="border-bottom: 1px solid #3f3f5a; padding-bottom: 10px; margin-bottom: 15px;">Executive Summary</h3>
        <div style="display: flex; justify-content: space-between;">
            <div style="width: 70%;">
                <p style="font-size: 16px; line-height: 1.6;">{results.llm_analysis.summary}</p>
                <div style="margin-top: 15px; font-weight: bold;">
                    <span style="background-color: {rec_color}; color: #1e1e2e; padding: 5px 10px; border-radius: 4px;">{recommendation}</span>
                    <span style="margin-left: 10px; color: #9e9e9e;">Fund Type: {fund_type}</span>
                </div>
            </div>
            <div style="width: 25%; background-color: #32324a; padding: 15px; border-radius: 8px;">
                <h4 style="margin-top: 0; font-size: 16px; text-align: center; margin-bottom: 15px;">Fund Profile</h4>
                <p><strong>Holdings:</strong> {results.holdings_count}</p>
                <p><strong>Top Sector:</strong> {top_sector}</p>
                <p><strong>Management Style:</strong> {sector_focus}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display key metrics using a dashboard-style layout
    st.markdown("""<div class="section-header">Key Performance Indicators</div>""", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Holdings", results.holdings_count, help="Total number of stocks in the fund")
    with col2:
        # Map the impact to a more detailed assessment for display
        impact_display_map = {
            "Strongly Positive": "Very Bullish",
            "Moderately Positive": "Bullish",
            "Neutral": "Neutral",
            "Moderately Negative": "Bearish",
            "Strongly Negative": "Very Bearish"
        }
        impact_display = impact_display_map.get(results.llm_analysis.impact, results.llm_analysis.impact)
        st.metric("Long-term Outlook", impact_display, help="AI-powered long-term market outlook assessment")
    
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
        st.metric("Near-term Sentiment", f"{impact_counts['Positive']}/{len(results.stock_analyses)}", 
                 delta_color="normal", delta=trend,
                 help="Ratio of stocks with positive news sentiment")
    
    # Add diversification score
    with col4:
        # Calculate diversification score based on sector concentration
        top_sectors = sorted(results.sector_exposure.items(), key=lambda x: x[1], reverse=True)
        top_sector_weight = top_sectors[0][1] if top_sectors else 0
        top_3_weight = sum(pct for _, pct in top_sectors[:3]) if len(top_sectors) >= 3 else 0
        
        if top_sector_weight > 45:
            div_score = "Low"
            delta = "down"
        elif top_sector_weight > 25 or top_3_weight > 70:
            div_score = "Moderate"
            delta = None
        else:
            div_score = "High"
            delta = "up"
        
        st.metric("Diversification", div_score, delta=delta, delta_color="normal",
                 help="Assessment of sector diversification")
    
    # Add sector representation gauge charts
    st.markdown("""<div class="section-header">Sector Allocation</div>""", unsafe_allow_html=True)
    
    def create_progress_bar(sector, percentage, max_pct=100):
        if percentage > 30:
            color = "#ff6b6b"  # Red for high concentration
        elif percentage > 15:
            color = "#ffe066"  # Yellow for medium concentration
        else:
            color = "#4ecdc4"  # Green for well-diversified
            
        return f"""
        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span>{sector}</span>
                <span>{percentage:.1f}%</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {(percentage/max_pct)*100}%; background-color: {color};"></div>
            </div>
        </div>
        """
    
    # Display top sectors with progress bars
    sector_cols = st.columns(2)
    
    # Calculate max percentage for scaling
    max_pct = max([pct for _, pct in top_sectors]) if top_sectors else 100
    max_pct = max(max_pct, 40)  # Ensure it's at least 40% for good scaling
    
    with sector_cols[0]:
        sectors_html = ""
        for sector, pct in top_sectors[:5]:
            sectors_html += create_progress_bar(sector, pct, max_pct)
        
        st.markdown(f"""
        <div style="background-color: #2d2d3f; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);">
            <h4 style="margin-top: 0; margin-bottom: 15px;">Top 5 Sectors</h4>
            {sectors_html}
        </div>
        """, unsafe_allow_html=True)
    
    with sector_cols[1]:
        # Display sector concentration metrics
        st.markdown(f"""
        <div style="background-color: #2d2d3f; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); height: 100%;">
            <h4 style="margin-top: 0; margin-bottom: 15px;">Concentration Analysis</h4>
            <div style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>Top Sector Weight</span>
                    <span>{top_sector_weight:.1f}%</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {top_sector_weight}%; background-color: {('#ff6b6b' if top_sector_weight > 30 else '#ffe066')};"></div>
                </div>
            </div>
            <div style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>Top 3 Sectors Weight</span>
                    <span>{top_3_weight:.1f}%</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {min(top_3_weight, 100)}%; background-color: {('#ff6b6b' if top_3_weight > 70 else '#ffe066' if top_3_weight > 50 else '#4ecdc4')};"></div>
                </div>
            </div>
            <div style="font-size: 0.9em; color: #9e9e9e; margin-top: 20px;">
                <p><strong>Fund Manager Note:</strong> {
                "High sector concentration increases risk exposure but may deliver outsized returns in favorable conditions." 
                if top_sector_weight > 30 else 
                "The fund maintains moderate sector diversification, providing balanced risk exposure."
                if top_3_weight > 50 else
                "Well-diversified sector allocation reduces specific sector risks but may limit outperformance."
                }</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Create tabs for different views with improved styling
    st.markdown("""<div class="section-header">Detailed Analysis</div>""", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["Fund Composition", "News Impact", "Investment Strategy", "Visualizations"])
    
    with tab1:
        # Display top holdings with improved table
        st.subheader("Top Holdings")
        holdings_data = []
        for holding in results.top_holdings[:10]:
            holdings_data.append({
                "Company": holding.name,
                "Ticker": holding.ticker or "N/A",
                "Sector": holding.sector or "N/A",
                "% of Fund": f"{holding.percentage:.2f}%"
            })
        
        # Add recommendation and growth potential indicators
        for i, holding in enumerate(holdings_data):
            # Simulate recommendation based on position
            if i < 3:
                holding["Recommendation"] = '<span class="badge-buy">BUY</span>'
            elif i < 7:
                holding["Recommendation"] = '<span class="badge-hold">HOLD</span>'
            else:
                if results.llm_analysis.impact in ["Strongly Negative", "Moderately Negative"]:
                    holding["Recommendation"] = '<span class="badge-sell">REDUCE</span>'
                else:
                    holding["Recommendation"] = '<span class="badge-hold">HOLD</span>'
        
        # Display as HTML table for better styling
        holdings_df = pd.DataFrame(holdings_data)
        st.markdown(holdings_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        # Add fund manager's note
        st.markdown("""
        <div class="fund-manager-note">
            <strong>Fund Manager's Note:</strong> The top holdings represent the highest conviction positions in the portfolio.
            Companies at the top of the list often have strong growth prospects, solid fundamentals, or strategic importance 
            to the fund's investment thesis.
        </div>
        """, unsafe_allow_html=True)
        
        # Display sector allocation
        st.subheader("Complete Sector Allocation")
        sector_data = []
        for sector, percentage in sorted(results.sector_exposure.items(), key=lambda x: x[1], reverse=True):
            sector_data.append({
                "Sector": sector,
                "Allocation": f"{percentage:.2f}%"
            })
        
        sector_df = pd.DataFrame(sector_data)
        st.table(sector_df)
    
    with tab2:
        # Display news impact with improved styling
        st.subheader("News Impact Analysis")
        
        # Add news sentiment summary card
        st.markdown(f"""
        <div style="background-color: #2d2d3f; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); margin-bottom: 20px;">
            <h4 style="margin-top: 0; margin-bottom: 15px;">News Sentiment Summary</h4>
            <div style="display: flex; justify-content: space-between; text-align: center;">
                <div>
                    <div style="font-size: 2rem; font-weight: bold; color: #4ecdc4;">{impact_counts['Positive']}</div>
                    <div>Positive</div>
                </div>
                <div>
                    <div style="font-size: 2rem; font-weight: bold; color: #ffe066;">{impact_counts['Neutral']}</div>
                    <div>Neutral</div>
                </div>
                <div>
                    <div style="font-size: 2rem; font-weight: bold; color: #ff6b6b;">{impact_counts['Negative']}</div>
                    <div>Negative</div>
                </div>
                <div>
                    <div style="font-size: 2rem; font-weight: bold;">{len(results.stock_analyses)}</div>
                    <div>Total</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Group by impact with collapsible sections
        for impact, color in [("Positive", "#4ecdc4"), ("Negative", "#ff6b6b"), ("Neutral", "#ffe066")]:
            impact_news = [a for a in results.stock_analyses if a.impact == impact]
            
            if impact_news:
                st.markdown(f"""
                <div style="margin-bottom: 20px;">
                    <div style="background-color: {color}; color: #1e1e2e; padding: 10px; border-radius: 5px 5px 0 0;">
                        <strong>{impact} Impact</strong> ({len(impact_news)} holdings)
                    </div>
                    <div style="border: 1px solid {color}; border-top: none; padding: 15px; border-radius: 0 0 5px 5px; background-color: #32324a;">
                """, unsafe_allow_html=True)
                
                news_data = []
                for analysis in impact_news:
                    news_data.append({
                        "Company": analysis.stock,
                        "Ticker": analysis.ticker,
                        "News": analysis.news_summary
                    })
                
                news_df = pd.DataFrame(news_data)
                st.table(news_df)
                
                st.markdown("</div></div>", unsafe_allow_html=True)
            else:
                st.info(f"No {impact.lower()} impact news found")
        
        # Add fund manager news interpretation
        if impact_counts["Positive"] > impact_counts["Negative"] * 2:
            news_narrative = "The overwhelmingly positive news sentiment suggests strong fundamental momentum across holdings."
        elif impact_counts["Positive"] > impact_counts["Negative"]:
            news_narrative = "The generally positive news environment provides favorable tailwinds for the fund's holdings."
        elif impact_counts["Negative"] > impact_counts["Positive"] * 2:
            news_narrative = "The concerning negative news pattern suggests potential fundamental challenges across multiple holdings."
        elif impact_counts["Negative"] > impact_counts["Positive"]:
            news_narrative = "The negative news bias warrants careful monitoring of underlying business conditions."
        else:
            news_narrative = "The balanced news environment suggests stable operating conditions across most holdings."
        
        st.markdown(f"""
        <div class="fund-manager-note">
            <strong>Fund Manager's Interpretation:</strong> {news_narrative}
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        # Display AI Investment Strategy Analysis with the enhanced display function
        display_llm_analysis(results.llm_analysis)
        
        # Add a section for portfolio strategy alignment
        st.markdown("### Portfolio Strategy Alignment")
        
        # Determine the investment style from the analysis
        is_growth_focused = any("growth" in r.lower() for r in results.llm_analysis.recommendations)
        is_defensive = any("defensive" in r.lower() for r in results.llm_analysis.recommendations)
        is_balanced = not is_growth_focused and not is_defensive
        
        # Create a gauge-like indicator for investment style
        style_cols = st.columns([1, 3, 1])
        with style_cols[1]:
            st.markdown("""
            <style>
            .investment-style-container {
                width: 100%;
                height: 40px;
                background: linear-gradient(to right, #ff6b6b, #ffe066, #4ecdc4);
                border-radius: 5px;
                position: relative;
                margin: 10px 0;
            }
            .investment-style-indicator {
                position: absolute;
                width: 10px;
                height: 30px;
                background-color: white;
                top: 5px;
                transform: translateX(-50%);
            }
            .investment-style-labels {
                display: flex;
                justify-content: space-between;
                margin-top: 5px;
                color: #e0e0e0;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Position the indicator based on the identified style
            position = "33%" if is_defensive else ("66%" if is_growth_focused else "50%")
            
            st.markdown(f"""
            <div class="investment-style-container">
                <div class="investment-style-indicator" style="left: {position};"></div>
            </div>
            <div class="investment-style-labels">
                <span>Defensive</span>
                <span>Balanced</span>
                <span>Growth</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Add a description of the portfolio's identified investment style
            if is_defensive:
                style_description = "This fund shows a defensive positioning that prioritizes capital preservation and stability over aggressive growth."
            elif is_growth_focused:
                style_description = "This fund employs a growth-oriented strategy focused on capital appreciation and higher potential returns with increased volatility."
            else:
                style_description = "This fund maintains a balanced approach that seeks moderate growth while managing downside risk."
            
            st.markdown(f"**Investment Style:** {style_description}")
        
        # Add a time horizon section
        st.markdown("### Recommended Investment Horizon")
        
        # Determine the appropriate time horizon based on the analysis
        has_long_term_catalysts = len(results.llm_analysis.opportunities) > 3
        has_structural_risks = any(("long-term" in r.lower() or "structural" in r.lower()) for r in results.llm_analysis.risks)
        
        if has_long_term_catalysts and not has_structural_risks:
            time_horizon = "Long-Term (5+ years)"
            horizon_description = "The fund's composition and sector exposures are well-positioned for long-term structural growth trends."
        elif has_structural_risks:
            time_horizon = "Medium-Term (2-5 years)"
            horizon_description = "While offering growth potential, some structural risks suggest a medium-term investment horizon with periodic reassessment."
        else:
            time_horizon = "Tactical (1-2 years)"
            horizon_description = "The current positioning may benefit from shorter-term market dynamics, warranting more frequent evaluation."
        
        st.info(f"**{time_horizon}**: {horizon_description}")
        
        # Macroeconomic sensitivity assessment
        st.markdown("### Macroeconomic Sensitivity")
        
        # Look for relevant keywords in the analysis
        interest_rate_sensitive = any("interest rate" in r.lower() for r in results.llm_analysis.risks + results.llm_analysis.recommendations)
        economic_cycle_sensitive = any("economic cycle" in r.lower() or "economic slowdown" in r.lower() for r in results.llm_analysis.risks + results.llm_analysis.recommendations)
        inflation_sensitive = any("inflation" in r.lower() for r in results.llm_analysis.risks + results.llm_analysis.recommendations)
        
        macro_cols = st.columns(3)
        with macro_cols[0]:
            sensitivity = "High" if interest_rate_sensitive else "Low"
            color = "#ff6b6b" if sensitivity == "High" else "#4ecdc4"
            st.markdown(f"**Interest Rate Sensitivity:** <span style='color:{color}'>{sensitivity}</span>", unsafe_allow_html=True)
        
        with macro_cols[1]:
            sensitivity = "High" if economic_cycle_sensitive else "Moderate"
            color = "#ff6b6b" if sensitivity == "High" else ("#ffe066" if sensitivity == "Moderate" else "#4ecdc4")
            st.markdown(f"**Economic Cycle Sensitivity:** <span style='color:{color}'>{sensitivity}</span>", unsafe_allow_html=True)
        
        with macro_cols[2]:
            sensitivity = "High" if inflation_sensitive else "Moderate"
            color = "#ff6b6b" if sensitivity == "High" else ("#ffe066" if sensitivity == "Moderate" else "#4ecdc4")
            st.markdown(f"**Inflation Sensitivity:** <span style='color:{color}'>{sensitivity}</span>", unsafe_allow_html=True)
        
        # Add recommended portfolio actions
        st.markdown("### Recommended Portfolio Actions")
        
        actions_cols = st.columns(2)
        with actions_cols[0]:
            st.markdown("""
            <div class="strategy-card" style="border-left: 4px solid #4ecdc4;">
                <h4 style="margin-top: 0;">Immediate Actions</h4>
                <ul>
                    <li>Review current allocations against the fund's long-term objectives</li>
                    <li>Assess exposure to sectors with negative outlook</li>
                    <li>Verify alignment with risk tolerance and investment time horizon</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with actions_cols[1]:
            st.markdown("""
            <div class="strategy-card" style="border-left: 4px solid #4e73df;">
                <h4 style="margin-top: 0;">Monitoring Priorities</h4>
                <ul>
                    <li>Track macroeconomic indicators affecting key sectors</li>
                    <li>Monitor quarterly performance of top holdings</li>
                    <li>Schedule regular portfolio reviews (quarterly)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Add fund manager final recommendation
        final_rec = "INCREASE ALLOCATION" if results.llm_analysis.impact in ["Strongly Positive", "Moderately Positive"] else ("MAINTAIN ALLOCATION" if results.llm_analysis.impact == "Neutral" else "REDUCE ALLOCATION")
        rec_reason = "The fund shows strong long-term growth potential with acceptable risk levels." if final_rec == "INCREASE ALLOCATION" else ("The fund demonstrates balanced risk-reward characteristics suitable for core portfolio allocation." if final_rec == "MAINTAIN ALLOCATION" else "The fund faces significant structural challenges that may impact long-term performance.")
        
        st.markdown(f"""
        <div style="background-color: #2d2d3f; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2); margin-top: 30px; border-left: 5px solid {'#4ecdc4' if final_rec == 'INCREASE ALLOCATION' else '#ffe066' if final_rec == 'MAINTAIN ALLOCATION' else '#ff6b6b'};">
            <h3 style="margin-top: 0;">Fund Manager's Recommendation</h3>
            <div style="display: flex; align-items: center; margin: 20px 0;">
                <div style="font-size: 1.5rem; font-weight: bold; padding: 10px 20px; background-color: {'#4ecdc4' if final_rec == 'INCREASE ALLOCATION' else '#ffe066' if final_rec == 'MAINTAIN ALLOCATION' else '#ff6b6b'}; color: #1e1e2e; border-radius: 5px;">
                    {final_rec}
                </div>
                <div style="margin-left: 20px; font-size: 1.1rem;">
                    {rec_reason}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with tab4:
        # Display visualizations
        st.subheader("Fund Analysis Visualizations")
        
        # Check if visualization files exist
        viz_dir = "visualizations"
        fund_name_safe = results.fund_name.replace(' ', '_')
        
        sector_pie = os.path.join(viz_dir, f"{fund_name_safe}_sector_pie.png")
        holdings_bar = os.path.join(viz_dir, f"{fund_name_safe}_top_holdings.png")
        impact_bar = os.path.join(viz_dir, f"{fund_name_safe}_impact.png")
        
        viz_cols = st.columns(2)
        
        with viz_cols[0]:
            if os.path.exists(sector_pie):
                st.image(sector_pie, caption="Sector Allocation")
                st.markdown("""
                <div style="font-size: 0.9em; color: #9e9e9e; margin-top: -15px;">
                    <p>Sector allocation visualization showing relative weights of different industries within the fund.</p>
                </div>
                """, unsafe_allow_html=True)
            
            if os.path.exists(impact_bar):
                st.image(impact_bar, caption="News Impact Distribution")
                st.markdown("""
                <div style="font-size: 0.9em; color: #9e9e9e; margin-top: -15px;">
                    <p>Distribution of news sentiment across fund holdings, indicating overall market perception.</p>
                </div>
                """, unsafe_allow_html=True)
        
        with viz_cols[1]:
            if os.path.exists(holdings_bar):
                st.image(holdings_bar, caption="Top Holdings")
                st.markdown("""
                <div style="font-size: 0.9em; color: #9e9e9e; margin-top: -15px;">
                    <p>Visualization of the fund's largest positions by percentage of total assets.</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Generate Excel file for download
    excel_path = results_to_excel(results, "mutual_fund")
    
    # Add styled download section
    st.markdown(f"""
    <div style="background-color: #2d2d3f; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2); margin-top: 30px; text-align: center;">
        <h3 style="margin-top: 0;">Download Full Analysis Report</h3>
        <p>Download the complete fund analysis with detailed metrics, holdings information, and investment recommendations.</p>
        <div style="margin-top: 15px;">
            {get_binary_file_downloader_html(excel_path, '<i class="fas fa-file-excel"></i> Download Excel Report')}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_llm_analysis(analysis):
    """Display the LLM analysis in a professional fund manager style"""
    st.markdown("## Strategic Investment Analysis")
    
    # Add impact indicator with more nuanced coloring
    impact_color = {
        "Strongly Positive": "#4ecdc4",  # Teal green
        "Moderately Positive": "#97e3d5", # Lighter teal
        "Neutral": "#ffe066",  # Yellow
        "Moderately Negative": "#ffb2b2", # Lighter red
        "Strongly Negative": "#ff6b6b",  # Red
    }.get(analysis.impact, "#4e73df")  # Default blue
    
    # Create a more professional-looking header section for fund manager perspective
    st.markdown(f"""
    <div style='padding: 20px; border-radius: 8px; background-color: #2d2d3f; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); margin-bottom: 25px; border-left: 6px solid {impact_color};'>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h3 style='margin: 0; color: {impact_color};'>Long-term Market Outlook</h3>
            <span style='padding: 5px 12px; background-color: {impact_color}; color: #1e1e2e; border-radius: 20px; font-weight: bold;'>{analysis.impact}</span>
        </div>
        <p style='font-size: 16px; line-height: 1.7; margin-bottom: 0;'>{analysis.summary}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a more structured layout for the recommendations, risks, and opportunities
    st.markdown("### Investment Strategy Framework")
    
    # Create toggle-able sections using expanders instead of tabs for a cleaner look
    with st.expander("Strategic Investment Recommendations", expanded=True):
        st.markdown("""
        <style>
        .recommendation-card {
            background-color: #32324a;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            border-left: 4px solid #4e73df;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='font-style: italic; color: #9e9e9e; margin-bottom: 20px;'>Professional recommendations based on comprehensive analysis of fund composition, sector trends, and macroeconomic factors:</p>", unsafe_allow_html=True)
        
        for i, rec in enumerate(analysis.recommendations, 1):
            st.markdown(f"""
            <div class='recommendation-card'>
                <h4 style='margin-top: 0; color: #4e73df; font-size: 1.1rem;'>Recommendation {i}</h4>
                <p style='margin-bottom: 0;'>{rec}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with st.expander("Risk Assessment Framework", expanded=True):
        st.markdown("""
        <style>
        .risk-card {
            background-color: #32324a;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            border-left: 4px solid #ff6b6b;
        }
        .risk-level {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            color: #1e1e2e;
            margin-left: 10px;
        }
        .risk-high {
            background-color: #ff6b6b;
        }
        .risk-medium {
            background-color: #ffe066;
        }
        .risk-low {
            background-color: #4ecdc4;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='font-style: italic; color: #9e9e9e; margin-bottom: 20px;'>Identified risk factors that may impact fund performance across different time horizons:</p>", unsafe_allow_html=True)
        
        for i, risk in enumerate(analysis.risks, 1):
            # Determine risk level based on keywords
            risk_level = "High" if any(kw in risk.lower() for kw in ["significant", "high", "substantial", "major"]) else \
                         "Low" if any(kw in risk.lower() for kw in ["minimal", "limited", "slight", "minor"]) else "Medium"
            
            risk_class = "risk-high" if risk_level == "High" else ("risk-medium" if risk_level == "Medium" else "risk-low")
            
            st.markdown(f"""
            <div class='risk-card'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                    <h4 style='margin: 0; color: #ff6b6b; font-size: 1.1rem;'>Risk Factor {i}</h4>
                    <span class='risk-level {risk_class}'>{risk_level} Risk</span>
                </div>
                <p style='margin-bottom: 0;'>{risk}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with st.expander("Growth Catalysts & Opportunities", expanded=True):
        st.markdown("""
        <style>
        .opportunity-card {
            background-color: #32324a;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            border-left: 4px solid #4ecdc4;
        }
        .opportunity-timeframe {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            color: #1e1e2e;
            margin-left: 10px;
        }
        .timeframe-short {
            background-color: #97e3d5;
        }
        .timeframe-medium {
            background-color: #4e73df;
        }
        .timeframe-long {
            background-color: #4ecdc4;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='font-style: italic; color: #9e9e9e; margin-bottom: 20px;'>Key growth opportunities identified through comprehensive analysis of market trends and fund positioning:</p>", unsafe_allow_html=True)
        
        for i, opp in enumerate(analysis.opportunities, 1):
            # Determine timeframe based on keywords
            timeframe = "Long-term" if any(kw in opp.lower() for kw in ["long-term", "sustained", "structural", "multi-year"]) else \
                        "Short-term" if any(kw in opp.lower() for kw in ["immediate", "short-term", "near-term", "current"]) else "Medium-term"
            
            timeframe_class = "timeframe-long" if timeframe == "Long-term" else ("timeframe-short" if timeframe == "Short-term" else "timeframe-medium")
            
            st.markdown(f"""
            <div class='opportunity-card'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                    <h4 style='margin: 0; color: #4ecdc4; font-size: 1.1rem;'>Growth Catalyst {i}</h4>
                    <span class='opportunity-timeframe {timeframe_class}'>{timeframe}</span>
                </div>
                <p style='margin-bottom: 0;'>{opp}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Add a professional fund manager summary box
    positive_aspects = len(analysis.opportunities)
    negative_aspects = len(analysis.risks)
    
    if analysis.impact in ["Strongly Positive", "Moderately Positive"]:
        summary_color = "#4ecdc4"
        summary_title = "Positive Investment Outlook"
        summary_icon = "📈"
    elif analysis.impact in ["Strongly Negative", "Moderately Negative"]:
        summary_color = "#ff6b6b"
        summary_title = "Cautious Investment Outlook"
        summary_icon = "📉"
    else:
        summary_color = "#ffe066"
        summary_title = "Neutral Investment Outlook"
        summary_icon = "📊"
    
    # Create a balanced assessment of the investment outlook
    if positive_aspects > negative_aspects * 1.5:
        outlook_statement = "The fund shows compelling long-term growth potential that outweighs identified risks."
    elif negative_aspects > positive_aspects * 1.5:
        outlook_statement = "Significant risk factors present substantial challenges to the fund's long-term performance potential."
    elif positive_aspects > negative_aspects:
        outlook_statement = "Growth opportunities moderately outweigh identified risks, suggesting a favorable risk-reward balance."
    elif negative_aspects > positive_aspects:
        outlook_statement = "Risk factors slightly outweigh identified opportunities, suggesting a cautious approach is warranted."
    else:
        outlook_statement = "The fund presents a balanced profile of opportunities and risks requiring regular reassessment."
    
    st.markdown(f"""
    <div style='background-color: #2d2d3f; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2); margin: 30px 0; border-top: 5px solid {summary_color};'>
        <h3 style='margin-top: 0;'>{summary_icon} {summary_title}</h3>
        <p style='font-size: 16px;'>{outlook_statement}</p>
        <div style='display: flex; margin-top: 20px; font-size: 0.9rem;'>
            <div style='flex: 1; padding-right: 15px; border-right: 1px solid #3f3f5a;'>
                <strong>Risk-Return Profile:</strong> {
                "Favorable" if analysis.impact in ["Strongly Positive", "Moderately Positive"] else 
                "Balanced" if analysis.impact == "Neutral" else 
                "Challenging"
                }
            </div>
            <div style='flex: 1; padding-left: 15px; padding-right: 15px; border-right: 1px solid #3f3f5a;'>
                <strong>Investor Suitability:</strong> {
                "Growth-oriented investors with higher risk tolerance" if analysis.impact in ["Strongly Positive", "Moderately Positive"] else 
                "Balanced investors seeking moderate growth" if analysis.impact == "Neutral" else 
                "Conservative investors with lower risk tolerance"
                }
            </div>
            <div style='flex: 1; padding-left: 15px;'>
                <strong>Recommended Review Frequency:</strong> {
                "Quarterly" if analysis.impact in ["Strongly Positive", "Moderately Positive"] else 
                "Semi-annually" if analysis.impact == "Neutral" else 
                "Monthly"
                }
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add investment horizon notice with better styling
    st.markdown("""
    <div style='background-color: #32324a; padding: 15px; border-radius: 8px; font-size: 0.9em; color: #9e9e9e; margin-top: 20px; border-left: 4px solid #4e73df;'>
        <strong>Analyst Disclosure:</strong> This analysis represents a point-in-time assessment based on current market conditions and fund composition. 
        All investments involve risk, including potential loss of principal. Past performance is not indicative of future results. 
        Investment horizons referenced are based on typical market cycles and structural economic trends. Individual investment decisions should 
        consider personal financial circumstances, objectives, and risk tolerance.
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main function for the Streamlit app"""
    # Display app header
    st.markdown('<div class="title-container"><h1>Professional Fund Manager Dashboard</h1><p>Comprehensive portfolio analysis and investment strategy platform with AI-powered insights</p></div>', unsafe_allow_html=True)
    
    # Create sidebar with professional navigation
    st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h3 style="color: #4e73df;">Investment Management Suite</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Main navigation
    app_mode = st.sidebar.selectbox(
        "Navigation", 
        ["Portfolio Analysis", "Market Research", "Investment Strategy", "Performance Tracking"]
    )
    
    if app_mode == "Portfolio Analysis":
        # Analysis type selection
        st.sidebar.markdown("""<div class="section-header">Analysis Type</div>""", unsafe_allow_html=True)
        analysis_type = st.sidebar.radio("Select Analysis Type", ["Mutual Fund Analysis", "Portfolio Analysis"])
        
        # API key configuration
        with st.sidebar.expander("API Configuration"):
            news_api_key = st.text_input("NewsAPI Key", value=os.getenv("NEWS_API_KEY", ""))
            if news_api_key:
                os.environ["NEWS_API_KEY"] = news_api_key
                st.success("News API key set!")
            else:
                st.warning("News API key is required for full functionality")
        
        # File upload section with professional styling
        st.sidebar.markdown("""<div class="section-header">Data Source</div>""", unsafe_allow_html=True)
        uploaded_file = st.sidebar.file_uploader("Upload Investment File", type="xlsx")
        
        # Sample files option
        st.sidebar.markdown("#### Sample Files")
        sample_files = []
        
        if analysis_type == "Mutual Fund Analysis":
            if os.path.exists("samples"):
                sample_files = [f for f in os.listdir("samples") if f.endswith(".xlsx") and "Fund" in f]
        else:
            if os.path.exists("samples"):
                sample_files = [f for f in os.listdir("samples") if f.endswith(".xlsx") and "portfolio" in f]
        
        selected_sample = st.sidebar.selectbox("Select a sample file", [""] + sample_files)
        
        # Analysis parameters section
        st.sidebar.markdown("""<div class="section-header">Analysis Parameters</div>""", unsafe_allow_html=True)
        time_horizon = st.sidebar.select_slider(
            "Investment Horizon",
            options=["Short-term", "Medium-term", "Long-term"],
            value="Long-term"
        )
        
        risk_profile = st.sidebar.select_slider(
            "Risk Tolerance",
            options=["Conservative", "Moderate", "Aggressive"],
            value="Moderate"
        )
        
        # Main content area with card styling
        if analysis_type == "Mutual Fund Analysis":
            st.markdown("""
            <div class="card">
                <h2 style="color: #4e73df;">Mutual Fund Analysis</h2>
                <p style="color: #e0e0e0;">Upload your mutual fund Excel file to analyze holdings, sector allocation, and long-term investment strategy recommendations.</p>
                <ul style="color: #e0e0e0;">
                    <li>Comprehensive sector analysis</li>
                    <li>Long-term growth assessment</li>
                    <li>Risk-adjusted strategy recommendations</li>
                    <li>Macroeconomic sensitivity evaluation</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card">
                <h2 style="color: #4e73df;">Stock Portfolio Analysis</h2>
                <p style="color: #e0e0e0;">Upload your stock portfolio Excel file to receive professional investment insights and strategic recommendations.</p>
                <ul style="color: #e0e0e0;">
                    <li>Stock-specific analysis and outlook</li>
                    <li>Portfolio composition evaluation</li>
                    <li>Risk assessment and diversification</li>
                    <li>Performance projections and optimization</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
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
        
        # Analyze button with professional styling
        if file_to_analyze:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                analyze_button = st.button(
                    "Generate Professional Analysis",
                    key="analyze_button", 
                    type="primary",
                    help="Click to perform comprehensive analysis with AI-powered insights"
                )
                
            if analyze_button:
                with st.spinner("Analyzing... Generating professional investment insights."):
                    try:
                        if analysis_type == "Mutual Fund Analysis":
                            # Add parameter hints
                            st.info(f"Analyzing with {time_horizon} investment horizon and {risk_profile} risk profile...")
                            
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
    
    elif app_mode == "Market Research":
        st.markdown('<div class="title-container"><h1>Market Research</h1><p>Explore market trends, sector analysis, and economic indicators</p></div>', unsafe_allow_html=True)
        st.info("Market Research functionality will be available in the next update.")
        
        # Placeholder for future market research functionality
        st.markdown("""
        <div class="card">
            <h3>Coming Soon: Comprehensive Market Research</h3>
            <p>This section will provide:</p>
            <ul>
                <li>Sector performance analysis</li>
                <li>Economic indicators tracking</li>
                <li>Market trend identification</li>
                <li>Global market correlations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    elif app_mode == "Investment Strategy":
        st.markdown('<div class="title-container"><h1>Investment Strategy Builder</h1><p>Create customized investment strategies based on your goals and market outlook</p></div>', unsafe_allow_html=True)
        st.info("Investment Strategy Builder will be available in the next update.")
        
        # Placeholder for future strategy builder functionality
        st.markdown("""
        <div class="card">
            <h3>Coming Soon: Strategy Builder</h3>
            <p>This section will allow you to:</p>
            <ul>
                <li>Define investment objectives</li>
                <li>Set allocation targets</li>
                <li>Create rebalancing rules</li>
                <li>Generate implementation plans</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    elif app_mode == "Performance Tracking":
        st.markdown('<div class="title-container"><h1>Performance Tracking</h1><p>Monitor your investment performance against benchmarks and goals</p></div>', unsafe_allow_html=True)
        st.info("Performance Tracking functionality will be available in the next update.")
        
        # Placeholder for future performance tracking functionality
        st.markdown("""
        <div class="card">
            <h3>Coming Soon: Performance Analytics</h3>
            <p>This section will provide:</p>
            <ul>
                <li>Return attribution analysis</li>
                <li>Risk-adjusted performance metrics</li>
                <li>Benchmark comparisons</li>
                <li>Historical performance tracking</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Add professional footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.markdown("""
    <div style="font-size:0.85em;">
    <p>The Professional Fund Manager Dashboard provides institutional-grade analysis tools for portfolio optimization and strategic investment planning.</p>
    
    <p><strong>Key Features:</strong></p>
    <ul>
        <li>AI-powered investment insights</li>
        <li>Sector and macroeconomic analysis</li>
        <li>Long-term investment strategy</li>
        <li>Risk assessment and management</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Version info
    st.sidebar.markdown("""
    <div style="text-align:center; margin-top:20px; font-size:0.8em; color:#9e9e9e;">
        Professional Fund Manager Suite v2.0<br>
        Powered by Advanced Analytics
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 