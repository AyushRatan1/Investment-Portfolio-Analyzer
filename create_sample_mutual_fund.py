#!/usr/bin/env python3
"""
Generate sample mutual fund holdings data for testing
"""

import pandas as pd
import os

def create_index_fund_sample():
    """Create a sample Nifty 50 index fund"""
    data = [
        {"Company Name": "Reliance Industries Ltd", "Symbol": "RELIANCE", "Sector": "Oil & Gas", "% of Net Assets": 11.5},
        {"Company Name": "HDFC Bank Ltd", "Symbol": "HDFCBANK", "Sector": "Banking", "% of Net Assets": 9.2},
        {"Company Name": "ICICI Bank Ltd", "Symbol": "ICICIBANK", "Sector": "Banking", "% of Net Assets": 8.1},
        {"Company Name": "Infosys Ltd", "Symbol": "INFY", "Sector": "IT Services", "% of Net Assets": 7.3},
        {"Company Name": "Tata Consultancy Services Ltd", "Symbol": "TCS", "Sector": "IT Services", "% of Net Assets": 5.9},
        {"Company Name": "Larsen & Toubro Ltd", "Symbol": "LT", "Sector": "Construction", "% of Net Assets": 4.3},
        {"Company Name": "Hindustan Unilever Ltd", "Symbol": "HINDUNILVR", "Sector": "FMCG", "% of Net Assets": 3.8},
        {"Company Name": "State Bank of India", "Symbol": "SBIN", "Sector": "Banking", "% of Net Assets": 3.5},
        {"Company Name": "Bharti Airtel Ltd", "Symbol": "BHARTIARTL", "Sector": "Telecom", "% of Net Assets": 3.2},
        {"Company Name": "ITC Ltd", "Symbol": "ITC", "Sector": "FMCG", "% of Net Assets": 3.1},
        {"Company Name": "Kotak Mahindra Bank Ltd", "Symbol": "KOTAKBANK", "Sector": "Banking", "% of Net Assets": 2.9},
        {"Company Name": "Axis Bank Ltd", "Symbol": "AXISBANK", "Sector": "Banking", "% of Net Assets": 2.7},
        {"Company Name": "Mahindra & Mahindra Ltd", "Symbol": "M&M", "Sector": "Automobile", "% of Net Assets": 2.5},
        {"Company Name": "Maruti Suzuki India Ltd", "Symbol": "MARUTI", "Sector": "Automobile", "% of Net Assets": 2.3},
        {"Company Name": "Tata Motors Ltd", "Symbol": "TATAMOTORS", "Sector": "Automobile", "% of Net Assets": 2.1},
        {"Company Name": "Asian Paints Ltd", "Symbol": "ASIANPAINT", "Sector": "Consumer Durables", "% of Net Assets": 1.9},
        {"Company Name": "Tata Steel Ltd", "Symbol": "TATASTEEL", "Sector": "Metals", "% of Net Assets": 1.8},
        {"Company Name": "Sun Pharmaceutical Industries Ltd", "Symbol": "SUNPHARMA", "Sector": "Pharmaceuticals", "% of Net Assets": 1.7},
        {"Company Name": "Coal India Ltd", "Symbol": "COALINDIA", "Sector": "Energy", "% of Net Assets": 1.6},
        {"Company Name": "Bajaj Finance Ltd", "Symbol": "BAJFINANCE", "Sector": "Financial Services", "% of Net Assets": 1.5}
    ]
    
    df = pd.DataFrame(data)
    
    # Ensure directory exists
    os.makedirs("samples", exist_ok=True)
    
    # Save to Excel
    output_file = "samples/Nifty50_Index_Fund.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Sample index fund created: {output_file}")

def create_technology_fund_sample():
    """Create a sample technology sector fund"""
    data = [
        {"Security": "Infosys Ltd", "ISIN": "INE009A01021", "Industry": "IT Services", "Weightage (%)": 13.5},
        {"Security": "Tata Consultancy Services Ltd", "ISIN": "INE467B01029", "Industry": "IT Services", "Weightage (%)": 12.8},
        {"Security": "Wipro Ltd", "ISIN": "INE075A01022", "Industry": "IT Services", "Weightage (%)": 8.5},
        {"Security": "HCL Technologies Ltd", "ISIN": "INE860A01027", "Industry": "IT Services", "Weightage (%)": 7.9},
        {"Security": "Tech Mahindra Ltd", "ISIN": "INE669C01036", "Industry": "IT Services", "Weightage (%)": 6.5},
        {"Security": "Bharti Airtel Ltd", "ISIN": "INE397D01024", "Industry": "Telecom", "Weightage (%)": 5.8},
        {"Security": "Tata Communications Ltd", "ISIN": "INE151A01013", "Industry": "Telecom", "Weightage (%)": 4.3},
        {"Security": "Persistent Systems Ltd", "ISIN": "INE262H01013", "Industry": "IT Services", "Weightage (%)": 3.9},
        {"Security": "LTIMindtree Ltd", "ISIN": "INE214T01019", "Industry": "IT Services", "Weightage (%)": 3.7},
        {"Security": "Tata Elxsi Ltd", "ISIN": "INE670A01012", "Industry": "IT Services", "Weightage (%)": 3.5},
        {"Security": "Mphasis Ltd", "ISIN": "INE356A01018", "Industry": "IT Services", "Weightage (%)": 3.2},
        {"Security": "Coforge Ltd", "ISIN": "INE591G01017", "Industry": "IT Services", "Weightage (%)": 2.9},
        {"Security": "Cyient Ltd", "ISIN": "INE136B01020", "Industry": "IT Services", "Weightage (%)": 2.6},
        {"Security": "Oracle Financial Services Software Ltd", "ISIN": "INE881D01027", "Industry": "Software", "Weightage (%)": 2.4},
        {"Security": "Sonata Software Ltd", "ISIN": "INE269A01021", "Industry": "Software", "Weightage (%)": 2.2},
        {"Security": "KPIT Technologies Ltd", "ISIN": "INE058I01045", "Industry": "IT Services", "Weightage (%)": 2.0},
        {"Security": "Indiamart Intermesh Ltd", "ISIN": "INE933S01016", "Industry": "E-Commerce", "Weightage (%)": 1.8},
        {"Security": "Zensar Technologies Ltd", "ISIN": "INE218A01016", "Industry": "IT Services", "Weightage (%)": 1.6},
        {"Security": "Intellect Design Arena Ltd", "ISIN": "INE306R01017", "Industry": "Software", "Weightage (%)": 1.5},
        {"Security": "Birlasoft Ltd", "ISIN": "INE836A01035", "Industry": "IT Services", "Weightage (%)": 1.4}
    ]
    
    df = pd.DataFrame(data)
    
    # Save to Excel
    output_file = "samples/Technology_Sector_Fund.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Sample technology fund created: {output_file}")

def create_banking_fund_sample():
    """Create a sample banking sector fund"""
    data = [
        {"Name": "HDFC Bank Ltd", "Code": "HDFCBANK", "Category": "Private Banking", "Weight": 16.8},
        {"Name": "ICICI Bank Ltd", "Code": "ICICIBANK", "Category": "Private Banking", "Weight": 14.5},
        {"Name": "State Bank of India", "Code": "SBIN", "Category": "Public Banking", "Weight": 12.3},
        {"Name": "Axis Bank Ltd", "Code": "AXISBANK", "Category": "Private Banking", "Weight": 10.7},
        {"Name": "Kotak Mahindra Bank Ltd", "Code": "KOTAKBANK", "Category": "Private Banking", "Weight": 8.9},
        {"Name": "IndusInd Bank Ltd", "Code": "INDUSINDBK", "Category": "Private Banking", "Weight": 6.5},
        {"Name": "Bandhan Bank Ltd", "Code": "BANDHANBNK", "Category": "Private Banking", "Weight": 4.8},
        {"Name": "Federal Bank Ltd", "Code": "FEDERALBNK", "Category": "Private Banking", "Weight": 4.2},
        {"Name": "Bank of Baroda", "Code": "BANKBARODA", "Category": "Public Banking", "Weight": 3.9},
        {"Name": "Punjab National Bank", "Code": "PNB", "Category": "Public Banking", "Weight": 3.1},
        {"Name": "IDFC First Bank Ltd", "Code": "IDFCFIRSTB", "Category": "Private Banking", "Weight": 2.8},
        {"Name": "AU Small Finance Bank Ltd", "Code": "AUBANK", "Category": "Private Banking", "Weight": 2.5},
        {"Name": "Canara Bank", "Code": "CANBK", "Category": "Public Banking", "Weight": 2.1},
        {"Name": "RBL Bank Ltd", "Code": "RBLBANK", "Category": "Private Banking", "Weight": 1.9},
        {"Name": "Bank of India", "Code": "BANKINDIA", "Category": "Public Banking", "Weight": 1.6},
        {"Name": "Indian Bank", "Code": "INDIANB", "Category": "Public Banking", "Weight": 1.3},
        {"Name": "Union Bank of India", "Code": "UNIONBANK", "Category": "Public Banking", "Weight": 1.2},
        {"Name": "IDBI Bank Ltd", "Code": "IDBI", "Category": "Public Banking", "Weight": 0.9},
    ]
    
    df = pd.DataFrame(data)
    
    # Save to Excel
    output_file = "samples/Banking_Sector_Fund.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Sample banking fund created: {output_file}")

if __name__ == "__main__":
    create_index_fund_sample()
    create_technology_fund_sample()
    create_banking_fund_sample()
    print("All sample mutual fund files created successfully.") 