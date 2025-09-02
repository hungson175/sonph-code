from fredapi import Fred
import os

# Get your FRED API key from https://fred.stlouisfed.org/docs/api/api_key.html
# Set it as environment variable: FRED_API_KEY=your_key_here

# Initialize Fred client
fred = Fred(api_key=os.environ.get('FRED_API_KEY'))

# Example: Get GDP data
try:
    gdp = fred.get_series('GDP')
    print("GDP data:")
    print(gdp.head())
    
    # Get series info
    gdp_info = fred.get_series_info('GDP')
    print("\nGDP series info:")
    print(f"Title: {gdp_info['title']}")
    print(f"Frequency: {gdp_info['frequency']}")
    print(f"Units: {gdp_info['units']}")
    
except Exception as e:
    print(f"Error: {e}")
    print("Make sure to set your FRED_API_KEY environment variable")