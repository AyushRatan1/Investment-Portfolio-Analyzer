import pandas as pd

# Sample portfolio data - mimicking a Groww export format
data = [
    {
        "Company Name": "Infosys Ltd",
        "Symbol": "INFY",
        "Sector": "IT Services",
        "Quantity": 10,
        "Avg Cost": 1450.25,
        "LTP": 1520.50
    },
    {
        "Company Name": "HDFC Bank Ltd",
        "Symbol": "HDFCBANK",
        "Sector": "Banking",
        "Quantity": 5,
        "Avg Cost": 1650.75,
        "LTP": 1680.25
    },
    {
        "Company Name": "Reliance Industries Ltd",
        "Symbol": "RELIANCE",
        "Sector": "Oil & Gas",
        "Quantity": 8,
        "Avg Cost": 2450.50,
        "LTP": 2520.75
    },
    {
        "Company Name": "Tata Consultancy Services Ltd",
        "Symbol": "TCS",
        "Sector": "IT Services",
        "Quantity": 3,
        "Avg Cost": 3550.25,
        "LTP": 3480.50
    },
    {
        "Company Name": "ITC Ltd",
        "Symbol": "ITC",
        "Sector": "FMCG",
        "Quantity": 20,
        "Avg Cost": 420.75,
        "LTP": 430.25
    }
]

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel file
output_file = "samples/sample_portfolio.xlsx"
df.to_excel(output_file, index=False)

print(f"Sample portfolio Excel file created: {output_file}")

# Create a different format (like Zerodha export) with different column names
zerodha_data = [
    {
        "Instrument": "Infosys Ltd",
        "Tradingsymbol": "INFY",
        "Type": "EQ",
        "Industry": "IT Services",
        "Qty.": 10,
        "Avg.": 1450.25,
        "Last Price": 1520.50
    },
    {
        "Instrument": "HDFC Bank Ltd",
        "Tradingsymbol": "HDFCBANK",
        "Type": "EQ",
        "Industry": "Banking",
        "Qty.": 5,
        "Avg.": 1650.75,
        "Last Price": 1680.25
    },
    {
        "Instrument": "Reliance Industries Ltd",
        "Tradingsymbol": "RELIANCE",
        "Type": "EQ",
        "Industry": "Oil & Gas",
        "Qty.": 8,
        "Avg.": 2450.50,
        "Last Price": 2520.75
    }
]

# Create DataFrame for Zerodha-like format
df_zerodha = pd.DataFrame(zerodha_data)

# Save to Excel file
zerodha_output_file = "samples/sample_zerodha_portfolio.xlsx"
df_zerodha.to_excel(zerodha_output_file, index=False)

print(f"Sample Zerodha-like portfolio Excel file created: {zerodha_output_file}") 