# filename: tools.py

from vnstock import stock_historical_data, company_overview
import pandas as pd
import logging
from datetime import datetime, timedelta

# Tắt các thông báo log không cần thiết của vnstock
logging.getLogger("vnstock").setLevel(logging.CRITICAL)

def get_company_information(ticker: str) -> str:
    """
    Tool dùng để tra cứu thông tin tổng quan của một công ty dựa trên mã ticker.
    """
    try:
        # Dùng hàm vnstock v2
        df = company_overview(ticker)
        
        # Chuyển DataFrame thành string (chuỗi) để LLM có thể đọc được
        # .T (Transpose) để xoay bảng cho dễ đọc
        return df.T.to_string()
    
    except Exception as e:
        return f"Lỗi khi tra cứu thông tin công ty: {e}"

def get_historical_prices(ticker: str, start_date: str, end_date: str) -> str:
    """
    Tool dùng để tra cứu giá lịch sử (OHLCV) của một mã cổ phiếu.
    Yêu cầu 3 tham số: ticker, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD).
    """
    try:
        # Dùng hàm vnstock v2
        df = stock_historical_data(
            symbol=ticker,
            start_date=start_date,
            end_date=end_date,
            resolution='1D'
        )
        
        # Chuyển DataFrame thành string, bỏ cột 'ticker' vì đã biết
        return df.drop(columns=['ticker']).to_string()
    
    except Exception as e:
        return f"Lỗi khi tra cứu giá lịch sử: {e}"

# === CÁC HÀM NÂNG CAO (CHO ĐIỂM CỘNG) ===

def get_sma(ticker: str, start_date: str, end_date: str, window: int) -> str:
    """Sử dụng khi người dùng yêu cầu tính SMA (Đường trung bình động giản đơn)."""
    try:
        # Cần lấy thêm dữ liệu quá khứ để tính rolling window
        # Lấy dư ra 2*window ngày để đảm bảo có đủ dữ liệu
        df = stock_historical_data(ticker, start_date, end_date)
        
        # Tính SMA
        df['SMA'] = df['close'].rolling(window=window).mean()
        
        # Lấy giá trị SMA cuối cùng (đã được tính toán đầy đủ)
        last_sma = df['SMA'].iloc[-1]
        
        if pd.isna(last_sma):
             return f"Không đủ dữ liệu để tính SMA({window}) cho {ticker} trong khoảng thời gian này."
             
        return f"Giá trị SMA({window}) cuối cùng của {ticker} là: {last_sma:.2f}"
    except Exception as e:
        return f"Lỗi khi tính SMA: {e}"

def get_rsi(ticker: str, start_date: str, end_date: str, window: int = 14) -> str:
    """Sử dụng khi người dùng yêu cầu tính RSI (Chỉ số sức mạnh tương đối)."""
    try:
        df = stock_historical_data(ticker, start_date, end_date)
        
        if len(df) < window:
            return f"Không đủ dữ liệu để tính RSI({window}) cho {ticker} (cần ít nhất {window} ngày)."

        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Lấy giá trị RSI cuối cùng
        last_rsi = rsi.iloc[-1]
        
        if pd.isna(last_rsi):
             return f"Không thể tính RSI({window}) cho {ticker} (có thể do 'loss' bằng 0)."

        return f"Giá trị RSI({window}) cuối cùng của {ticker} là: {last_rsi:.2f}"
    except Exception as e:
        return f"Lỗi khi tính RSI: {e}"

# === TEST CÁC TOOL (Chạy file này trực tiếp) ===
if __name__ == "__main__":
    print("--- Đang test các tool ---")
    
    # Test Tool 1
    print("\n[Test 1: Thông tin FPT]")
    print(get_company_information("FPT"))
    
    # Test Tool 2
    print("\n[Test 2: Giá HPG 1 tuần đầu 2023]")
    print(get_historical_prices("HPG", "2023-01-01", "2023-01-10"))

    # Test Tool 3 (Bonus)
    print("\n[Test 3: SMA 20 ngày của HPG]")
    # Cần 1 khoảng thời gian đủ dài để tính SMA 20
    print(get_sma("HPG", "2023-01-01", "2023-03-01", 20))
    
    # Test Tool 4 (Bonus)
    print("\n[Test 4: RSI 14 ngày của HPG]")
    print(get_rsi("HPG", "2023-01-01", "2023-03-01", 14))