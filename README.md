# Investment Portfolio Analysis AI Agent

This AI agent analyzes your stock portfolio and mutual funds, providing comprehensive news insights and impact assessments.

## Features

- **Excel Import**: Automatically extracts stock and mutual fund information from Excel files
- **Intelligent News Analysis**: Finds the most relevant news for each stock or fund holding
- **Impact Assessment**: Evaluates whether news is likely to have a positive, negative, or neutral impact
- **AI-Driven Analysis**: Uses intelligent algorithms to provide detailed investment insights
- **Mutual Fund Breakdown**: Analyzes mutual funds by their holdings composition and sector allocation
- **Visual Analytics**: Generates charts and graphs to visualize your investments
- **Interactive Mode**: User-friendly interface to choose your portfolio file and see analysis results
- **Modern Web Interface**: Clean, responsive UI for a great user experience
- **Excel Export**: Download detailed analysis results in Excel format

## Setup

1. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

2. **API Keys**:
   
   **News API (Required for news analysis)**:
   - Sign up for a free API key at [News API](https://newsapi.org/)
   - Free tier includes 100 requests/day
   
   **Note**: The system now includes a built-in analysis engine and no longer requires an external LLM API.

3. **Configure API Keys**:
   - Open the `.env` file
   - Update the API keys:
     ```
     NEWS_API_KEY=your_actual_api_key
     ```
   - Alternatively, you can enter your API keys interactively when running the analyzers

## Usage

### Web Interface

The easiest way to use the tool is through the web interface:

```
streamlit run portfolio_analyzer_app.py
```

This opens a modern, user-friendly web app where you can:
- Upload your own Excel files or use sample files
- Choose between mutual fund or portfolio analysis
- View interactive analysis results with charts and tables
- Download Excel reports with comprehensive analysis data

### Excel-to-Excel Command Line Tool

For quick analysis without the web interface, use:

```
python excel_analyzer.py samples/Technology_Sector_Fund.xlsx
```

Options:
- `--output/-o`: Specify the output Excel file path
- `--type/-t`: Force analysis type (`portfolio`, `mutual_fund`, or `auto`)
- `--api-key/-k`: Specify NewsAPI key

Example:
```
python excel_analyzer.py samples/sample_portfolio.xlsx --output my_analysis.xlsx --type portfolio
```

### CLI Mutual Fund Analysis

```
python3 analyze_mutual_fund.py
```

The interactive mutual fund analyzer will:
1. Guide you through selecting a mutual fund Excel file
2. Analyze the fund's holdings, sector allocation, and news impact
3. Generate visualizations of the fund composition
4. Provide AI-driven insights, recommendations, and risk assessment
5. Save detailed results to a JSON file

### CLI Stock Portfolio Analysis

```
python3 analyze_portfolio.py
```

The interactive stock portfolio analyzer will:
1. Help you select a portfolio Excel file
2. Analyze news for each stock in your portfolio
3. Evaluate the potential impact of each news item
4. Save detailed results to a JSON file

### Creating Sample Files

Generate sample mutual fund data for testing:
```
python3 create_sample_mutual_fund.py
```

Generate sample stock portfolio data for testing:
```
python3 create_sample_portfolio.py
```

## Excel Format Support

### For Mutual Funds

The analyzer intelligently detects common mutual fund disclosure formats:

- Fund holdings (company names, tickers)
- Allocation percentages (in any format: 0-1 or 0-100)
- Sector classifications

### For Stock Portfolios

Supports various formats from trading platforms like Groww and Zerodha.

## Analysis Output

### Mutual Fund Analysis

- **Sector Allocation**: Breakdown of the fund by industry sectors
- **Top Holdings**: Companies with the largest allocation in the fund
- **News Impact**: Assessment of recent news for each holding
- **AI Analysis**: Summary, impact assessment, recommendations
- **Risk Analysis**: Identification of key risks to watch
- **Opportunities**: Potential opportunities based on current news

### Stock Portfolio Analysis

- **News Summaries**: Recent news for each stock in your portfolio
- **Impact Assessment**: Positive, negative, or neutral ratings
- **Additional Headlines**: Extra news items for deeper analysis

## Visualizations

The mutual fund analyzer generates:
- Sector allocation pie charts
- Top holdings bar charts
- News impact distribution charts

## Technical Notes

- Uses Pydantic for data validation and modeling
- Implements an algorithmic approach for investment insights
- Leverages matplotlib and seaborn for data visualization
- Modern Streamlit web interface for interactive analysis
- Excel export functionality for detailed reports 