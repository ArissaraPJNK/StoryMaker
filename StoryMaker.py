import streamlit as st
from openai import OpenAI
import pandas as pd

# ตั้งค่า Sidebar
st.sidebar.title("NLP Story Generator")
api_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password")
if api_key:
    client = OpenAI(api_key=api_key)

# ส่วนหลักของแอป
st.title("10-Line Story Generator")
st.write("กรอกคีย์เวิร์ดเพื่อสร้างนิทาน 10 บรรทัด")

# รับคีย์เวิร์ดจากผู้ใช้
keywords = st.text_input("คีย์เวิร์ด (เช่น มังกร, เจ้าหญิง, ภูเขาไฟ):")

# เพิ่มตัวเลือกสำหรับสไตล์นิทาน
style = st.selectbox("เลือกสไตล์ของนิทาน", ["ตลก", "ดราม่า", "ผจญภัย", "สยองขวัญ"])

if st.button("สร้างนิทาน"):
    if not keywords:
        st.error("กรุณากรอกคีย์เวิร์ด")
    elif not api_key:
        st.error("กรุณากรอก API Key ใน Sidebar")
    else:
        # Prompt สำหรับแต่งนิทาน
        thai_prompt = f"เขียนนิทาน 10 บรรทัดโดยใช้คำต่อไปนี้: {keywords} และให้มีสไตล์ {style}"

        try:
            # เรียกใช้ ChatGPT API สำหรับนิทานภาษาไทย
            response_thai = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": thai_prompt}]
            )
            # แก้ไขการเข้าถึงข้อมูลใน response
            story_thai = response_thai.choices[0].message.content

            # Prompt สำหรับแปลภาษา
            english_prompt = f"Translate the following Thai story into English:\n\n{story_thai}"
            response_english = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": english_prompt}]
            )
            # แก้ไขการเข้าถึงข้อมูลใน response
            story_english = response_english.choices[0].message.content

            # แสดงผล
            st.subheader("นิทานภาษาไทย")
            st.write(story_thai)
            st.subheader("นิทานภาษาอังกฤษ")
            st.write(story_english)

            # ดาวน์โหลดผลลัพธ์
            data = pd.DataFrame({"ภาษาไทย": [story_thai], "ภาษาอังกฤษ": [story_english]})
            csv = data.to_csv(index=False).encode("utf-8")
            st.download_button("ดาวน์โหลดผลลัพธ์ (CSV)", data=csv, file_name="story.csv", mime="text/csv")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
