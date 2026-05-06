from flask import Flask, request, send_file
import fitz
import os
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def translate(text):
    if not text.strip():
        return ""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "翻譯英文成繁體中文，保留專業術語與格式"},
                {"role": "user", "content": text}
            ]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"[翻譯錯誤] {str(e)}"

@app.route("/")
def home():
    return '''
    <h2>PDF翻譯</h2>
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
    new_doc = fitz.open()

    for page in doc:
        text = page.get_text()

        if not text.strip():
            text = "（此頁無可讀文字）"

        translated = translate(text)

        new_page = new_doc.new_page()
        new_page.insert_text((50, 50), translated)

    output_path = "output.pdf"
    new_doc.save(output_path)

    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
