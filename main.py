
from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

FILE_NAME = "data.xlsx"

@app.route("/api/upload-file", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "fail", "message": "ไม่พบไฟล์ในคำขอ"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"status": "fail", "message": "ชื่อไฟล์ว่าง"}), 400

    try:
        file.save(FILE_NAME)
        return jsonify({"status": "success", "message": f"อัปโหลดไฟล์ {FILE_NAME} สำเร็จ!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def search_product(keyword):
    try:
        df = pd.read_excel(FILE_NAME, skiprows=9, usecols="E,F,I,J")
    except FileNotFoundError:
        return "ไม่พบไฟล์ข้อมูล กรุณาอัปโหลดไฟล์ก่อน"

    result = df[df["สินค้า"].str.contains(keyword, case=False, na=False)]
    if result.empty:
        return "ขออภัย ไม่พบสินค้าที่ค้นหาในระบบ"

    row = result.iloc[0]
    return f"พบแล้วค่ะ: {row['ไลน์ที่']} {row['สินค้า']} ราคา {row['ราคา']} บาท เหลือ {row['มี Stock อยู่ที่']} ชิ้น"

@app.route("/callback", methods=["POST"])
def callback():
    body = request.json
    try:
        events = body["events"]
        for event in events:
            if event["type"] == "message" and event["message"]["type"] == "text":
                user_msg = event["message"]["text"]
                reply_token = event["replyToken"]
                if user_msg.startswith("ค้นหา"):
                    keyword = user_msg.replace("ค้นหา", "").strip()
                    answer = search_product(keyword)
                    return jsonify({"status": "ok", "reply": answer})
                else:
                    return jsonify({"status": "ignored"}), 200
        return jsonify({"status": "no_event"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "ระบบพร้อมทำงานแล้ว!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
