# 📊 VnStock AI Agent - Trợ lý Chứng khoán Thông minh

Dự án xây dựng AI Agent có khả năng trả lời các câu hỏi về thị trường chứng khoán Việt Nam, sử dụng **LangChain**, **VnStock API**, và **FastAPI**.

---

## 🎯 Tính năng chính

Agent có khả năng:
- ✅ Tra cứu thông tin tổng quan về công ty (ticker, ngành, số nhân viên, website...)
- ✅ Lấy dữ liệu giá lịch sử (OHLCV) của cổ phiếu
- ✅ Tính toán chỉ báo kỹ thuật SMA (Simple Moving Average)
- ✅ Tính toán chỉ báo kỹ thuật RSI (Relative Strength Index)
- ✅ Hiểu ngữ cảnh thời gian tương đối ("hôm qua", "3 tháng gần nhất", "tuần trước"...)
- ✅ Trả lời bằng tiếng Việt tự nhiên, dễ hiểu

---

## 📁 Cấu trúc dự án

```
VnStockAgent/
├── main.py                              # FastAPI server (endpoint /chat)
├── agent.py                             # Khởi tạo LangChain Agent với tools
├── tools.py                             # Các hàm nghiệp vụ gọi VnStock API
├── test_api.py                          # Script pytest để test tự động
├── AI_Intern_test_questions.json       # File câu hỏi test (ground truth)
├── .env                                 # File chứa API keys (KHÔNG nộp file này!)
├── requirements.txt                     # Danh sách thư viện Python
└── README.md                            # File này
```

---

## 🚀 Hướng dẫn cài đặt

### **Bước 1: Clone/Download dự án**
```bash
# Giải nén file VnStockAgent.zip hoặc clone từ repository
cd VnStockAgent
```

### **Bước 2: Tạo môi trường ảo Python**
```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt môi trường ảo
# Windows:
.\venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### **Bước 3: Cài đặt thư viện**
```bash
pip install -r requirements.txt
```

### **Bước 4: Cấu hình API Key**
Tạo file `.env` trong thư mục gốc với nội dung:

```ini
OPENROUTER_API_KEY=sk-or-v1-YOUR_OPENROUTER_KEY_HERE
MODEL_NAME=kwaipilot/kat-coder-pro:free
```

**Lưu ý:** 
- Bạn cần đăng ký tài khoản tại [OpenRouter.ai](https://openrouter.ai/) để lấy API key
- Model `kwaipilot/kat-coder-pro:free` là model miễn phí, bạn có thể thay bằng model khác nếu muốn

---

## 🎮 Hướng dẫn sử dụng

### **1. Chạy API Server**

Mở terminal và chạy:
```bash
uvicorn main:app --reload
```

Server sẽ khởi động tại: `http://127.0.0.1:8000`

### **2. Test API qua Swagger UI**

Truy cập: `http://127.0.0.1:8000/docs`

Bạn sẽ thấy giao diện Swagger để test endpoint `/chat`:
- Click vào `/chat` → **Try it out**
- Nhập câu hỏi vào field `question`, ví dụ: `"Thông tin về công ty FPT?"`
- Click **Execute**

### **3. Test bằng Python**

Bạn có thể test trực tiếp bằng script:
```bash
python agent.py
```

Script sẽ chạy 3 test cases mẫu.

### **4. Test API bằng cURL**

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"question": "Giá cổ phiếu HPG hôm qua là bao nhiêu?"}'
```

---

## 🧪 Chạy Test Tự động (Pytest)

Đây là phần **quan trọng nhất** của bài test, đánh giá độ chính xác của Agent.

### **Bước 1: Đảm bảo server đang chạy**
```bash
# Terminal 1: Chạy server
uvicorn main:app --reload
```

### **Bước 2: Chạy pytest**
```bash
# Terminal 2: Chạy test
pytest -v -s
```

### **Kết quả mong đợi:**
```
test_api.py::test_agent_with_json_questions PASSED
======================== 4 passed in 55.03s ========================
```

**Giải thích:**
- `4 passed`: Tất cả 4 câu hỏi trong `AI_Intern_test_questions.json` đã được trả lời đúng
- Agent hiểu được "hôm qua" là ngày cuối tuần (2025-11-15)
- Agent tìm đúng công ty "Tập đoàn Hòa Phát" khi hỏi về HPG

---

## 📝 Ví dụ câu hỏi

Agent có thể trả lời các câu hỏi như:

### **Thông tin công ty:**
```
Q: "Cho tôi biết thông tin về công ty FPT"
A: [Thông tin chi tiết về FPT: ticker, sàn, ngành nghề, số nhân viên...]
```

### **Giá lịch sử:**
```
Q: "Giá cổ phiếu HPG hôm qua là bao nhiêu?"
A: "Giá cổ phiếu HPG ngày 15/11/2025: Open 26,500, Close 26,900..."
```

### **Khoảng thời gian tương đối:**
```
Q: "Cho tôi giá VNM trong 3 tháng gần nhất"
A: [Bảng giá từ 19/08/2025 đến 17/11/2025 với phân tích xu hướng]
```

### **Chỉ báo kỹ thuật:**
```
Q: "Tính SMA 20 ngày của FPT trong 6 tháng qua"
A: "Giá trị SMA(20) cuối cùng của FPT là: 99,720 VNĐ"
```

---

## 🛠️ Công nghệ sử dụng

| Thư viện | Phiên bản | Mục đích |
|----------|-----------|----------|
| **langchain** | 0.3.14 | Framework chính để xây dựng AI Agent |
| **langchain-openai** | 0.2.14 | Tích hợp OpenAI-compatible LLM |
| **langchain-classic** | 0.3.4 | Tool calling agent (create_tool_calling_agent) |
| **fastapi** | 0.115.6 | Web framework để xây dựng API |
| **uvicorn** | 0.34.0 | ASGI server để chạy FastAPI |
| **vnstock** | 2.2.1 | Thư viện lấy dữ liệu chứng khoán VN |
| **pytest** | 8.3.4 | Framework để test tự động |

---

## 🏗️ Kiến trúc hệ thống

```
┌─────────────┐
│   USER      │
│  (Client)   │
└──────┬──────┘
       │
       │ HTTP POST /chat
       ↓
┌─────────────────────────────────────────┐
│         FastAPI Server (main.py)        │
│  - Nhận request                          │
│  - Gọi AgentExecutor                     │
│  - Trả về response                       │
└────────────────┬────────────────────────┘
                 │
                 │ invoke()
                 ↓
┌─────────────────────────────────────────┐
│    LangChain Agent (agent.py)           │
│  - Phân tích câu hỏi                     │
│  - Quyết định tool nào cần dùng         │
│  - Gọi tool với tham số đúng            │
│  - Tổng hợp kết quả thành câu trả lời   │
└────────────────┬────────────────────────┘
                 │
                 │ tool_call()
                 ↓
┌─────────────────────────────────────────┐
│       Business Tools (tools.py)         │
│  - get_company_information()            │
│  - get_historical_prices()              │
│  - get_sma()                             │
│  - get_rsi()                             │
└────────────────┬────────────────────────┘
                 │
                 │ API call
                 ↓
┌─────────────────────────────────────────┐
│         VnStock API (vnstock)           │
│  - company_overview()                    │
│  - stock_historical_data()              │
└─────────────────────────────────────────┘
```

---

## 🔧 Cách Agent hoạt động

### **1. Tool Calling với StructuredTool**
Agent sử dụng `StructuredTool` từ LangChain để:
- Tự động parse nhiều tham số từ type hints
- Validate input trước khi gọi function
- Truyền đúng số lượng tham số cho mỗi tool

### **2. Xử lý thời gian tương đối**
Agent được prompt với ngày hiện tại và ví dụ tính toán:
```python
system_message = f"""
Ngày hôm nay là: {today}
Ví dụ:
- "3 tháng gần nhất" = từ {today - 90 days} đến {today}
- "hôm qua" = {today - 1 day}
"""
```

### **3. Tự động retry và error handling**
- `max_iterations=10`: Agent có tối đa 10 lần thử
- `handle_parsing_errors=True`: Tự động xử lý lỗi parse
- `verbose=True`: In ra quá trình suy luận (hữu ích khi debug)

---

## 📊 Kết quả Test

Dự án đã pass **100% test cases** với các tiêu chí:

✅ **Độ chính xác về thời gian:**
- Hiểu "hôm qua" là ngày 15/11/2025 (cuối tuần)
- Tự tính toán "3 tháng gần nhất" = từ 19/08/2025 đến 17/11/2025

✅ **Độ chính xác về dữ liệu:**
- Tìm đúng công ty "Tập đoàn Hòa Phát" cho ticker HPG
- Lấy đúng giá đóng cửa: 26,900 VNĐ

✅ **Xử lý tool calling:**
- Gọi đúng tool với đúng tham số
- Không bị lỗi thiếu tham số

---

## ⚠️ Lưu ý quan trọng

### **1. File .env không được nộp**
File `.env` chứa API key riêng của bạn và **KHÔNG BAO GIỜ** được đưa vào git hoặc nộp bài.

### **2. Rate Limit**
Model miễn phí `kwaipilot/kat-coder-pro:free` có giới hạn request. Nếu gặp lỗi 429, hãy:
- Đợi 1-2 phút trước khi thử lại
- Hoặc đổi sang model khác (có phí)

### **3. Dữ liệu VnStock**
Dữ liệu từ VnStock có thể không có cho:
- Ngày cuối tuần (thị trường không giao dịch)
- Ngày lễ
- Ticker không tồn tại

Agent sẽ thông báo rõ ràng trong những trường hợp này.

---

## 🐛 Troubleshooting

### **Lỗi: ModuleNotFoundError**
```bash
# Đảm bảo đã kích hoạt venv và cài đặt đủ thư viện
pip install -r requirements.txt
```

### **Lỗi: 429 Rate Limit**
```
Đợi 1-2 phút hoặc thay đổi MODEL_NAME trong .env
```

### **Test không pass**
```bash
# Kiểm tra server có đang chạy không
curl http://127.0.0.1:8000/

# Xem log chi tiết
pytest -v -s --tb=short
```

---

## 👨‍💻 Tác giả

**Thông tin sinh viên:**
- Tên: Nguyễn Công Thắng
- Email: congthangws04@gmail.com

**Dự án:** Bài test AI Agent Chứng khoán VnStock
**Ngày hoàn thành:** 17/11/2025

---

## 📜 License

Dự án này được tạo ra cho mục đích học tập và đánh giá kỹ năng.

---

## 🙏 Tài liệu tham khảo

- [LangChain Documentation](https://python.langchain.com/)
- [VnStock Documentation](https://github.com/thinh-vu/vnstock)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenRouter API](https://openrouter.ai/docs)