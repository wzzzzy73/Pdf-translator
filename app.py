from flask import Flask, request, send_file, jsonify
import fitz
from openai import OpenAI
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def translate(text):
    if not text.strip():
        return ""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是專業翻譯，將英文精準翻譯成繁體中文，保留專業術語"},
            {"role": "user", "content": text}
        ]
    )
    return res.choices[0].message.content

@app.route("/")
def home():
    return '''
    <h2>PDF 翻譯系統</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="pdf">
        <button type="submit">上傳</button>
    </form>
    '''

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["pdf"]
    file.save("input.pdf")

    doc = fitz.open("input.pdf")

    result = []
    out = fitz.open()

    for i, page in enumerate(doc):
        text = page.get_text()

        zh = translate(text)

        # 📌 回傳給前端（頁數+原文+翻譯）
        result.append({
            "page": i+1,
            "original": text,
            "translated": zh
        })

        # 📄 建立新PDF（不排版版）
        p = out.new_page()
        p.insert_text((50, 50),
            f"Page {i+1}\n\nOriginal:\n{text}\n\nTranslated:\n{zh}"
        )

    out.save("output.pdf")

    return send_file("output.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
