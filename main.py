# filename: main.py

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date

# Import "người chạy" Agent từ file agent.py của bạn
# Rất quan trọng: file này phải tên là agent.py và chứa biến agent_executor
try:
    from agent import agent_executor
except ImportError:
    print("LỖI: Không tìm thấy file agent.py hoặc biến agent_executor.")
    print("Hãy chắc chắn bạn đã tạo file agent.py thành công.")
    exit()

# --- 1. ĐỊNH NGHĨA CẤU TRÚC INPUT/OUTPUT ---

# Định nghĩa cấu trúc JSON mà API sẽ nhận vào
# Nó phải chứa một trường tên là "question"
class Query(BaseModel):
    question: str

# Định nghĩa cấu trúc JSON mà API sẽ trả về
# Nó phải chứa một trường tên là "answer"
class Answer(BaseModel):
    answer: str

# --- 2. KHỞI TẠO APP FASTAPI ---
app = FastAPI(
    title="VnStock AI Agent API",
    description="API cho phép hỏi đáp thông tin tài chính Việt Nam (dùng VnStock & LangChain)",
    version="1.0.0"
)

print("✅ Đã khởi tạo FastAPI thành công.")
print("Agent đã sẵn sàng nhận câu hỏi qua API...")

# --- 3. TẠO ENDPOINT /ask ---

# Đây là "cửa" để nhận câu hỏi
# Nó chỉ chấp nhận phương thức POST
@app.post("/ask", response_model=Answer)
async def ask_agent(query: Query):
    """
    Nhận câu hỏi của người dùng, đưa cho Agent xử lý và trả về câu trả lời.
    """

    # Lấy ngày hôm nay để đưa vào prompt của Agent
    today = date.today().strftime('%Y-%m-%d')

    print(f"\n[API] Nhận được câu hỏi: {query.question}")

    try:
        # Gọi Agent để xử lý câu hỏi
        # Chúng ta truyền input và ngày hôm nay, giống hệt file test agent.py
        result = agent_executor.invoke({
            "input": query.question,
            "current_date": today
        })

        # Lấy câu trả lời cuối cùng từ Agent
        final_answer = result['output']
        print(f"[API] Trả lời: {final_answer[:50]}...") # In 50 ký tự đầu

        # Trả về câu trả lời theo đúng định dạng JSON
        return Answer(answer=final_answer)

    except Exception as e:
        print(f"[API] LỖI: {e}")
        # Trả về một câu trả lời lỗi (nhưng vẫn đúng cấu trúc JSON)
        return Answer(answer=f"Đã xảy ra lỗi khi xử lý câu hỏi của bạn: {e}")

# Thêm một endpoint gốc (/) để kiểm tra API có "sống" không
@app.get("/")
def read_root():
    return {"message": "Chào mừng đến với VnStock AI Agent API! Hãy dùng endpoint /docs để xem tài liệu."}