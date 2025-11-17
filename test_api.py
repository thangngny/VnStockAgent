# filename: test_api.py

import pytest
import requests 
import json
from datetime import date, timedelta

# Import các tool gốc của vnstock v2 để lấy "sự thật"
from vnstock import company_overview, stock_historical_data

# Địa chỉ API của bạn (đang chạy trên máy)
API_URL = "http://127.0.0.1:8000/ask"

# Hàm để tải các câu hỏi test
def load_test_questions():
    try:
        with open('AI_Intern_test_questions.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        pytest.fail("LỖI: Không tìm thấy file AI_Intern_test_questions.json")
    except json.JSONDecodeError:
        pytest.fail("LỖI: File AI_Intern_test_questions.json bị lỗi cú pháp JSON.")

# Lấy dữ liệu test
test_data = load_test_questions()

# --- BỘ TEST TỰ ĐỘNG ---

@pytest.mark.parametrize("test_case", test_data)
def test_agent_accuracy(test_case):
    question = test_case["question"]
    ticker = test_case["ticker"]
    test_type = test_case["type"]
    
    print(f"\n--- Đang test: {question} ---")
    
    # --- 1. LẤY "SỰ THẬT" (GROUND TRUTH) ---
    expected_value = None
    
    if test_type == "info":
        try:
            df = company_overview(ticker)
            expected_value = df['shortName'].iloc[0] 
        except Exception as e:
            pytest.fail(f"Lỗi khi lấy ground truth cho {ticker}: {e}")
            
    elif test_type == "price_today":
        try:
            today = date.today()
            start_date = today - timedelta(days=5) # Lấy 5 ngày gần nhất
            df = stock_historical_data(ticker, start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
            
            if not df.empty:
                expected_value = str(df['close'].iloc[-1]) # Giá cuối cùng
            else:
                # Nếu 5 ngày qua không giao dịch, 'expected_value' sẽ là None
                expected_value = None 
                
        except Exception as e:
            pytest.fail(f"Lỗi khi lấy ground truth cho {ticker}: {e}")

    if test_type != "price_today" and expected_value is None:
         pytest.fail(f"Không xác định được 'expected_value' cho test case: {question}")

    print(f"[Ground Truth] Giá trị kỳ vọng cho {ticker} là: {expected_value}")

    # --- 2. GỌI API AGENT CỦA BẠN ---
    try:
        response = requests.post(API_URL, json={"question": question})
        response.raise_for_status() 
        
        agent_answer = response.json().get('answer')
        if agent_answer is None:
            pytest.fail("API không trả về trường 'answer'")
            
    except requests.RequestException as e:
        pytest.fail(f"Lỗi khi gọi API: {e}")
        
    print(f"[Agent Answer] Câu trả lời của Agent: {agent_answer[:100]}...")

    # --- 3. SO SÁNH (LOGIC ĐÃ SỬA) ---
    
    if test_type == "price_today":
        today = date.today()
        # .weekday() (Thứ 2 = 0, Thứ 3 = 1, ... Chủ Nhật = 6)
        yesterday_weekday = (today - timedelta(days=1)).weekday()
        # 5 = T7, 6 = CN
        yesterday_is_weekend = (yesterday_weekday >= 5) 

        if yesterday_is_weekend:
            # HÔM NAY LÀ T2 (HOẶC CN), "HÔM QUA" LÀ CUỐI TUẦN
            print(f"[Test Logic] 'Hôm qua' ({today - timedelta(days=1)}) là cuối tuần.")
            # Agent PHẢI BÁO là không có dữ liệu
            assert "không có dữ liệu" in agent_answer.lower() or \
                   "cuối tuần" in agent_answer.lower() or \
                   "ngày nghỉ" in agent_answer.lower()
            print(f"✅ PASSED: Agent đã nhận diện đúng là ngày nghỉ.")
        else:
            # HÔM NAY LÀ NGÀY THƯỜNG (T3-T7)
            print(f"[Test Logic] 'Hôm qua' ({today - timedelta(days=1)}) là ngày giao dịch.")
            if expected_value:
                 # Agent PHẢI TRẢ VỀ ĐÚNG SỐ
                assert str(expected_value).lower() in agent_answer.lower()
                print(f"✅ PASSED: '{expected_value}' đã có trong câu trả lời.")
            else:
                pytest.fail("Lỗi logic: 'Hôm qua' là ngày giao dịch nhưng không tìm thấy 'expected_value'")
    
    elif test_type == "info":
        # Logic test info (đã chạy đúng)
        assert str(expected_value).lower() in agent_answer.lower()
        print(f"✅ PASSED: '{expected_value}' đã có trong câu trả lời.")