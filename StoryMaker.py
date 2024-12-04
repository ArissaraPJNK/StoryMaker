import streamlit as st
import openai
import pandas as pd

# ตั้งค่า Sidebar
st.sidebar.title("NLP Story Generator")
api_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password")
if api_key:
    openai.api_key = api_key

# ส่วนหลักของแอป
st.title("10-Line Story Generator")
st.write("กรอกคีย์เวิร์ดเพื่อสร้างนิทาน 10 บรรทัด")

# รับคีย์เวิร์ดจากผู้ใช้
keywords = st.text_input("คีย์เวิร์ด (เช่น มังกร, เจ้าหญิง, ภูเขาไฟ):")

# เพิ่มตัวเลือกสำหรับสไตล์นิทาน
style = st.selectbox("เลือกสไตล์ของนิทาน", ["ตลก", "ดราม่า", "ผจญภัย"])

if st.button("สร้างนิทาน"):
    if not keywords:
        st.error("กรุณากรอกคีย์เวิร์ด")
    elif not api_key:
        st.error("กรุณากรอก API Key ใน Sidebar")
    else:
        # Prompt สำหรับแต่งนิทาน
        thai_prompt = f"เขียนนิทาน 10 บรรทัดโดยใช้คำต่อไปนี้: {keywords} และให้มีสไตล์ {style}"

        try:
            # เรียกใช้ ChatGPT API เพื่อแต่งนิทาน
            response = openai.ChatCompletion.create(
                model="gpt-4",  # หรือ "gpt-3.5-turbo" หากคุณใช้ Plus หรือไม่มี GPT-4
                messages=[
                    {"role": "system", "content": "คุณเป็นนักเขียนนิทาน"},
                    {"role": "user", "content": thai_prompt}
                ]
            )
            story_thai = response["choices"][0]["message"]["content"]

            # Prompt สำหรับแปลภาษา
            english_prompt = f"Translate the following Thai story into English:\n\n{story_thai}"
            response = openai.ChatCompletion.create(
                model="gpt-4",  # หรือ "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "You are a translator who translates Thai stories into English"},
                    {"role": "user", "content": english_prompt}
                ]
            )
            story_english = response["choices"][0]["message"]["content"]

            # แสดงผล
            st.subheader("นิทานภาษาไทย")
            st.write(story_thai)
            st.subheader("นิทานภาษาอังกฤษ")
            st.write(story_english)

            # ดาวน์โหลดผลลัพธ์
            data = pd.DataFrame({"ภาษาไทย": [story_thai], "ภาษาอังกฤษ": [story_english]})
            csv = data.to_csv(index=False).encode("utf-8")
            st.download_button("ดาวน์โหลดผลลัพธ์ (CSV)", data=csv, file_name="story.csv", mime="text/csv")
        except openai.error.OpenAIError as e:
            st.error(f"เกิดข้อผิดพลาดจาก OpenAI API: {e}")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
