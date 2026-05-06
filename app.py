from flask import Flask, request, send_file
import fitz
import os
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def translate(text):
    res = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "把英文翻譯成繁體中文，保留專業術語"},
            {"role": "user", "content": text}
        ]
    )
    return res.choices[0].message.content

@app.route("/", methods=["GET"])
def home():
    return '''
    <h2>PDF 翻譯</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="pdf">
        <button type="submit">上傳翻譯</button>
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
        translated = translate(text)

        p = new_doc.new_page()
        p.insert_text((50,50), translated)

    new_doc.save("output.pdf")
    return send_file("output.pdf", as_attachment=True)

app.run(host="0.0.0.0", port=10000)
