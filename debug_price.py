
import os
import sys

# Mocking environment variables to test
# os.environ["TWELVE_DATA_API_KEY"] = "demo" # Try with 'demo' key if applicable, or leave empty to see error

try:
    from external_client import get_price
    print(f"Price: {get_price()}")
except Exception as e:
    print(f"Error: {e}")
