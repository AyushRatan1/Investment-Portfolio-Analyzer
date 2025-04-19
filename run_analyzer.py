#!/usr/bin/env python3
"""
Setup and Run Script for Portfolio Analyzer
Handles dependencies installation and launches the web interface
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path
import argparse

def install_dependencies():
    """Install required dependencies from requirements.txt"""
    print("Checking and installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        # Also install BeautifulSoup for the news fetcher
        print("Installing additional dependencies for multi-source news fetcher...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
        
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {str(e)}")
        return False

def check_api_key():
    """Check if NewsAPI key is configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    news_api_key = os.getenv("NEWS_API_KEY")
    
    if not news_api_key:
        print("\nWARNING: No NewsAPI key found in .env file.")
        print("News analysis functionality may be limited.")
        
        setup_key = input("Would you like to enter your NewsAPI key now? (y/n): ").lower()
        if setup_key == 'y':
            news_api_key = input("Enter your NewsAPI.org API key: ").strip()
            
            # Update or create .env file
            with open(".env", "w") as f:
                f.write(f"NEWS_API_KEY={news_api_key}\n")
            
            print("API key saved to .env file.")
        else:
            print("Continuing without API key. News analysis will be limited.")

def create_sample_files():
    """Create sample files for testing if needed"""
    samples_dir = Path("samples")
    
    if not samples_dir.exists() or not any(samples_dir.glob("*.xlsx")):
        print("\nNo sample files found. Creating sample files...")
        
        # Create samples directory
        samples_dir.mkdir(exist_ok=True)
        
        # Import and run sample creation functions
        try:
            from create_sample_mutual_fund import create_index_fund_sample, create_technology_fund_sample, create_banking_fund_sample
            from create_sample_portfolio import create_samples
            
            # Create mutual fund samples
            create_index_fund_sample()
            create_technology_fund_sample()
            create_banking_fund_sample()
            
            # Create portfolio samples (function name might differ, try both conventions)
            try:
                create_samples()
            except:
                # The function might not exist, try to run the script directly
                subprocess.check_call([sys.executable, "create_sample_portfolio.py"])
            
            print("Sample files created successfully.")
        except Exception as e:
            print(f"Error creating sample files: {str(e)}")
    else:
        print("Sample files already exist.")

def ensure_folders_exist():
    """Ensure required directories exist"""
    for folder in ["visualizations", "uploads", "downloads"]:
        os.makedirs(folder, exist_ok=True)

def run_web_interface():
    """Launch the Streamlit web interface"""
    print("\nLaunching web interface...")
    port = 8501  # Default Streamlit port
    
    # Open browser after a short delay to make sure Streamlit has started
    def open_browser():
        time.sleep(2)
        webbrowser.open(f"http://localhost:{port}")
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run Streamlit
    try:
        subprocess.check_call([sys.executable, "-m", "streamlit", "run", "portfolio_analyzer_app.py"])
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error running web interface: {str(e)}")

def run_excel_analyzer(input_file, output_file=None, analysis_type="auto"):
    """Run Excel-to-Excel analysis"""
    print(f"\nAnalyzing {input_file}...")
    
    cmd = [sys.executable, "excel_analyzer.py", input_file]
    
    if output_file:
        cmd.extend(["--output", output_file])
    
    if analysis_type != "auto":
        cmd.extend(["--type", analysis_type])
    
    try:
        subprocess.check_call(cmd)
        print("Analysis complete!")
    except subprocess.CalledProcessError as e:
        print(f"Error during analysis: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    """Main function to setup and run the analyzer"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Setup and run Portfolio Analyzer')
    parser.add_argument('--excel', '-e', help='Excel file to analyze (skips web interface)')
    parser.add_argument('--output', '-o', help='Output Excel file (used with --excel)')
    parser.add_argument('--type', '-t', choices=['portfolio', 'mutual_fund', 'auto'], 
                       default='auto', help='Analysis type (used with --excel)')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    parser.add_argument('--skip-setup', action='store_true', help='Skip dependencies installation')
    
    args = parser.parse_args()
    
    # Print welcome message
    print("=" * 70)
    print("Investment Portfolio Analyzer Setup".center(70))
    print("=" * 70)
    
    # Install dependencies if needed
    if not args.skip_setup:
        if not install_dependencies():
            print("Failed to install dependencies. Exiting.")
            return 1
    
    # Check API key
    check_api_key()
    
    # Create sample files if needed
    create_sample_files()
    
    # Ensure required folders exist
    ensure_folders_exist()
    
    # Either run Excel analyzer or web interface
    if args.excel:
        if os.path.exists(args.excel):
            run_excel_analyzer(args.excel, args.output, args.type)
        else:
            print(f"Error: Excel file not found: {args.excel}")
            return 1
    else:
        # Only disable auto-open if explicitly specified
        if args.no_browser:
            # Run streamlit directly
            subprocess.check_call([sys.executable, "-m", "streamlit", "run", "portfolio_analyzer_app.py"])
        else:
            run_web_interface()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 