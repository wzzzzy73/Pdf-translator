from flask import Flask, request, send_file
import fitz
import os
from openai import OpenAI

app = Flask(__name__)

# 📌 限制檔案大小（5MB）
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# 📌 OpenAI API Key（從 Render 環境變數讀）
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# -----------------------
# 翻譯函式
# -----------------------
def translate(text):
    try:
        if not text or not text.strip():
            return ""

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "你是專業翻譯，將英文精準翻譯成繁體中文，保留專業術語"
                },
                {
                    "role": "user",
                    "content": text[:1000]  # 避免太長爆掉
                }
            ]
        )

        return res.choices[0].message.content

    except Exception as e:
        return f"[翻譯錯誤] {str(e)}"

# -----------------------
# 首頁
# -----------------------
@app.route("/")
def home():
    return '''
    <h2>PDF 翻譯系統</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="pdf" required>
        <button type="submit">上傳 PDF</button>
    </form>
    '''

# -----------------------
# 上傳 + 翻譯
# -----------------------
@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files["pdf"]
        file.save("input.pdf")

        doc = fitz.open("input.pdf")
        new_doc = fitz.open()

        for i, page in enumerate(doc):
            text = page.get_text()

            if not text:
                text = "（此頁無可讀文字）"

            translated = translate(text)

            page_out = new_doc.new_page()
            page_out.insert_text(
                (50, 50),
                f"Page {i+1}\n\n原文:\n{text[:500]}\n\n---\n\n翻譯:\n{translated}"
            )

        output_path = "output.pdf"
        new_doc.save(output_path)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"❌ 系統錯誤：{str(e)}"

# -----------------------
# 啟動（Render 用）
# -----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
