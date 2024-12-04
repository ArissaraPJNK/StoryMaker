import streamlit as st
from openai import OpenAI
import pandas as pd

# ตั้งค่า Sidebar
st.sidebar.title("NLP Story Generator")
api_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password")
if api_key:
    client = OpenAI(api_key=api_key)

# ส่วนหลักของแอป
st.title("นิทานฝึกภาษา")
st.write("กรอกคีย์เวิร์ดเพื่อสร้างนิทานสั้นแสนสนุก")

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
        thai_prompt = f"เขียนนิทานไม่เกิน 15 บรรทัดโดยใช้คำต่อไปนี้: {keywords} และให้มีสไตล์ {style} โดยนิทานต้องมีเนื้อเรื่องที่สมเหตุสมผล คำนึงถึงองค์ประกอบละครทั้ง 6 ของอริสโตเติล และใช้ภาษาที่สละสลวย"

        try:
            # เรียกใช้ ChatGPT API สำหรับนิทานภาษาไทย
            response_thai = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": thai_prompt}]
            )
            story_thai = response_thai.choices[0].message.content

            # Prompt สำหรับแปลภาษา
            english_prompt = f"Translate the following Thai story into English:\n\n{story_thai}"
            response_english = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": english_prompt}]
            )
            story_english = response_english.choices[0].message.content

            # แสดงผล
            st.subheader("นิทานภาษาไทย")
            st.write(story_thai)
            st.subheader("นิทานภาษาอังกฤษ")
            st.write(story_english)

             # เพิ่มฟังก์ชันในการค้นหาคำศัพท์ที่มีระดับความยาก A2 ขึ้นไป
            vocabulary_prompt = f"Identify words in the following text that are at least A2 level and provide the following details: Word, Part of Speech, Thai translation:\n\n{story_english}"
            response_vocab = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": vocabulary_prompt}]
            )

            vocabulary_data = response_vocab.choices[0].message.content

            # แสดงคำศัพท์ในรูปแบบตาราง
            vocab_list = []
            for line in vocabulary_data.split("\n"):
                if line.strip():  # กรองบรรทัดที่ไม่ใช่คำศัพท์
                    word_info = line.split(",")  # สมมุติว่าเราจะแยกคำและข้อมูลในแต่ละบรรทัด
                    if len(word_info) >= 3:  # ตรวจสอบว่าแต่ละบรรทัดมีข้อมูลครบ
                        word = word_info[0].strip()
                        part_of_speech = word_info[1].strip()
                        thai_translation = word_info[2].strip()
                        vocab_list.append({"Word": word, "Part of Speech": part_of_speech, "Thai Translation": thai_translation})

            if vocab_list:
                vocab_df = pd.DataFrame(vocab_list)
                st.subheader("คำศัพท์ที่มีระดับความยาก A2 ขึ้นไป")
                st.dataframe(vocab_df)

            # ดาวน์โหลดผลลัพธ์
            data = pd.DataFrame({"ภาษาไทย": [story_thai], "ภาษาอังกฤษ": [story_english]})
            csv = data.to_csv(index=False).encode("utf-8")
            st.download_button("ดาวน์โหลดผลลัพธ์ (CSV) ภาษาไทย-อังกฤษ", data=csv, file_name="story.csv", mime="text/csv", key="download_story_csv")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")


