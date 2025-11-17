# IMPORT THEO CÁCH CỦA V2
from vnstock import stock_historical_data, company_overview
import pandas as pd
import logging

logging.getLogger("vnstock").setLevel(logging.CRITICAL)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# === 1. THÔNG TIN CÔNG TY (Cách V2) ===
print("--- 1. THÔNG TIN CÔNG TY (FPT) ---")
try:
    # V2 dùng hàm lẻ, không cần 'source'
    overview_data = company_overview('FPT') 
    print(type(overview_data))
    print(overview_data)
except Exception as e:
    print(f"Loi: {e}")

print("\n" + "="*30 + "\n")

# === 2. GIÁ LỊCH SỬ (Cách V2) ===
print("--- 2. GIÁ LỊCH SỬ (HPG) ---")
try:
    # V2 dùng hàm lẻ, dùng 'start_date' và 'end_date'
    price_data = stock_historical_data(
        symbol='HPG',
        start_date='2023-01-01',
        end_date='2023-04-01',
        resolution='1D'
    )
    
    print(type(price_data))
    print(price_data.head())
except Exception as e:
    print(f"Loi: {e}")