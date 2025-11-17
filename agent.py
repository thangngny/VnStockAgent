import os
from dotenv import load_dotenv
from datetime import date, timedelta
from typing import Optional

# LangChain imports - FIXED CHO LANGCHAIN 1.0.7+
from langchain_core.tools import StructuredTool  # ⭐ THAY ĐỔI: Dùng StructuredTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# ⭐ THAY ĐỔI QUAN TRỌNG: Import từ langchain_classic thay vì langchain
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

# Import các tool của chúng ta từ file tools.py
from tools import (
    get_company_information, 
    get_historical_prices, 
    get_sma, 
    get_rsi
)

# --- 1. TẢI API KEY VÀ KHỞI TẠO LLM ---

# Tải key từ file .env
load_dotenv()

# Kiểm tra xem key API đã được tải chưa
if not os.getenv("OPENROUTER_API_KEY"):
    raise EnvironmentError("OPENROUTER_API_KEY chưa được set trong file .env")

# Đọc MODEL_NAME từ file .env
MODEL_NAME = os.getenv("MODEL_NAME")
if not MODEL_NAME:
    raise EnvironmentError("MODEL_NAME chưa được set trong file .env")

# Khởi tạo LLM ("bộ não")
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model=MODEL_NAME,
    temperature=0.0
)

print("✅ Đã khởi tạo LLM thành công.")

# --- 2. "GÓI" CÁC TOOLS LẠI CHO LANGCHAIN (DÙNG StructuredTool) ---

# ⭐ Tạo các wrapper functions với type hints rõ ràng
def tool_get_company_info(ticker: str) -> str:
    """Tra cứu thông tin tổng quan về một công ty."""
    return get_company_information(ticker)

def tool_get_historical_prices(ticker: str, start_date: str, end_date: str) -> str:
    """Tra cứu giá cổ phiếu lịch sử trong khoảng thời gian."""
    return get_historical_prices(ticker, start_date, end_date)

def tool_get_sma(ticker: str, start_date: str, end_date: str, window: int) -> str:
    """Tính toán SMA (Simple Moving Average) trong khoảng thời gian."""
    return get_sma(ticker, start_date, end_date, window)

def tool_get_rsi(ticker: str, start_date: str, end_date: str, window: int = 14) -> str:
    """Tính toán RSI (Relative Strength Index) trong khoảng thời gian."""
    return get_rsi(ticker, start_date, end_date, window)

# Tạo danh sách tools với StructuredTool
tools = [
    StructuredTool.from_function(
        func=tool_get_company_info,
        name="TraCuuThongTinCongTy",
        description="""Rất hữu ích khi người dùng hỏi thông tin chung về một công ty. 
                       Cần 1 tham số:
                       - ticker: Mã chứng khoán (ví dụ: 'FPT', 'HPG')"""
    ),
    StructuredTool.from_function(
        func=tool_get_historical_prices,
        name="TraCuuGiaLichSu",
        description="""Rất hữu ích khi người dùng hỏi về giá cổ phiếu trong khoảng thời gian.
                       Cần 3 tham số:
                       - ticker: Mã chứng khoán (ví dụ: 'HPG')
                       - start_date: Ngày bắt đầu (định dạng 'YYYY-MM-DD')
                       - end_date: Ngày kết thúc (định dạng 'YYYY-MM-DD')"""
    ),
    StructuredTool.from_function(
        func=tool_get_sma,
        name="TinhToanSMA",
        description="""Sử dụng khi người dùng yêu cầu tính SMA (Đường trung bình động giản đơn).
                       Cần 4 tham số:
                       - ticker: Mã chứng khoán
                       - start_date: Ngày bắt đầu (định dạng 'YYYY-MM-DD')
                       - end_date: Ngày kết thúc (định dạng 'YYYY-MM-DD')
                       - window: Số ngày tính trung bình (số nguyên, ví dụ: 20)"""
    ),
    StructuredTool.from_function(
        func=tool_get_rsi,
        name="TinhToanRSI",
        description="""Sử dụng khi người dùng yêu cầu tính RSI (Chỉ số sức mạnh tương đối).
                       Cần 3 tham số (window mặc định là 14):
                       - ticker: Mã chứng khoán
                       - start_date: Ngày bắt đầu (định dạng 'YYYY-MM-DD')
                       - end_date: Ngày kết thúc (định dạng 'YYYY-MM-DD')
                       - window: (Tùy chọn) Số ngày tính RSI, mặc định 14"""
    )
]

print(f"✅ Đã tải {len(tools)} tools thành công.")

# --- 3. TẠO PROMPT (LỜI CHỈ DẪN) CHO AGENT ---

# Lấy ngày hôm nay để đưa vào system prompt
today = date.today().strftime('%Y-%m-%d')

# Lấy ngày hôm nay để đưa vào system prompt
today = date.today().strftime('%Y-%m-%d')

system_message = f"""
Bạn là một trợ lý tài chính chuyên nghiệp tại thị trường Việt Nam. 
Bạn phải trả lời câu hỏi của người dùng một cách chính xác.
Bạn phải luôn sử dụng các công cụ được cung cấp khi được hỏi về dữ liệu.
Không được tự bịa ra số liệu.

QUAN TRỌNG: 
- Ngày hôm nay là: {today}
- Khi người dùng hỏi các khoảng thời gian tương đối (ví dụ: 'hôm qua', 'tuần trước', '3 tháng gần nhất'),
  BẠN phải tự tính toán ra 'start_date' và 'end_date' chính xác dựa trên ngày hôm nay.
- Luôn dùng định dạng 'YYYY-MM-DD' cho ngày tháng khi gọi Tools.
- Khi trả lời, hãy tóm tắt kết quả từ tool một cách thân thiện và rõ ràng.

*** QUY TẮC NGHIÊM NGẶT VỀ "HÔM QUA" ***
- Khi người dùng hỏi "hôm qua" (yesterday), BẠN PHẢI TÍNH TOÁN VÀ CHỈ TÌM DỮ LIỆU CHO ĐÚNG NGÀY ĐÓ.
- Nếu tool trả về "không có dữ liệu" (vì ngày đó là cuối tuần hoặc ngày lễ),
  bạn PHẢI báo cho người dùng là "Không có dữ liệu giao dịch cho ngày... vì là ngày nghỉ."
- TUYỆT ĐỐI KHÔNG được tự ý tìm ngày giao dịch gần nhất (như hôm nay hoặc thứ Sáu) để thay thế.

Ví dụ tính toán thời gian:
- "3 tháng gần nhất" = từ {(date.today() - timedelta(days=90)).strftime('%Y-%m-%d')} đến {today}
- "6 tháng qua" = từ {(date.today() - timedelta(days=180)).strftime('%Y-%m-%d')} đến {today}
- "tuần trước" = từ {(date.today() - timedelta(days=7)).strftime('%Y-%m-%d')} đến {today}
"""

# Tạo prompt template cho tool calling agent
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# --- 4. TẠO AGENT VÀ AGENT EXECUTOR ---

# Tạo agent với create_tool_calling_agent (từ langchain_classic)
agent = create_tool_calling_agent(llm, tools, prompt)

# Tạo AgentExecutor (từ langchain_classic)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10,
    return_intermediate_steps=False
)

print("✅ Đã tạo Agent Executor thành công.")
print("--- Sẵn sàng nhận câu hỏi ---")

# --- 5. TEST AGENT (Chạy file này trực tiếp) ---
if __name__ == "__main__":
    
    print(f"\n{'='*50}")
    print(f"🗓️  Ngày hôm nay: {today}")
    print(f"{'='*50}")

    print("\n--- [Test 1: Hỏi thông tin FPT] ---")
    question1 = "Thông tin về công ty FPT?"
    try:
        result1 = agent_executor.invoke({"input": question1})
        print(f"\n✅ Câu trả lời: {result1['output']}\n")
    except Exception as e:
        print(f"❌ Lỗi: {e}\n")
    
    print(f"\n{'-'*50}")
    print("\n--- [Test 2: Hỏi giá 3 tháng gần nhất] ---")
    question2 = "Cho tôi biết giá cổ phiếu HPG trong 3 tháng gần nhất"
    try:
        result2 = agent_executor.invoke({"input": question2})
        print(f"\n✅ Câu trả lời: {result2['output']}\n")
    except Exception as e:
        print(f"❌ Lỗi: {e}\n")

    print(f"\n{'-'*50}")
    print("\n--- [Test 3: Hỏi SMA] ---")
    question3 = "Tính SMA 20 ngày của FPT trong 6 tháng qua"
    try:
        result3 = agent_executor.invoke({"input": question3})
        print(f"\n✅ Câu trả lời: {result3['output']}\n")
    except Exception as e:
        print(f"❌ Lỗi: {e}\n")
    
    print(f"\n{'='*50}")
    print("✅ Hoàn thành tất cả test!")
    print(f"{'='*50}")