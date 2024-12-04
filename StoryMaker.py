import streamlit as st
from openai import OpenAI
import pandas as pd
import nltk
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet

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

            # วิเคราะห์คำศัพท์
            def get_vocabulary_analysis(text):
                # Tokenize และแท็กคำศัพท์
                tokens = word_tokenize(text)
                pos_tags = pos_tag(tokens)

                # เลือกคำศัพท์ที่เป็นระดับ A2 ขึ้นไป (สมมุติว่าระบุคำด้วยเงื่อนไขนี้)
                vocabulary = []
                for word, tag in pos_tags:
                    # ตัวอย่างการคัดกรอง (ปรับแต่งได้)
                    if len(word) > 3:  # สมมุติว่าใช้ความยาว > 3 เป็นตัวกรอง
                        word_translation_prompt = f"Translate this English word into Thai: {word}"
                        translation_response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": word_translation_prompt}]
                        )
                        thai_translation = translation_response.choices[0].message.content
                            if "translates to Thai as" in thai_translation:
                            thai_translation = thai_translation.split("translates to Thai as")[1].strip()

                        # ขั้นที่สอง: ตัดคำในวงเล็บ (เช่น "(pronounced: bpăa)")
                            import re
                            thai_translation = re.sub(r'\(.*\)', '', thai_translation).strip()

                        vocabulary.append({"Word": word, "POS": tag, "Translation": thai_translation})

                return pd.DataFrame(vocabulary)

            vocab_df = get_vocabulary_analysis(story_english)

            # แสดงผล
            st.subheader("นิทานภาษาไทย")
            st.write(story_thai)
            st.subheader("นิทานภาษาอังกฤษ")
            st.write(story_english)
            st.subheader("คำศัพท์สำคัญ")
            st.dataframe(vocab_df)

            # ดาวน์โหลดผลลัพธ์
            data = pd.DataFrame({"ภาษาไทย": [story_thai], "ภาษาอังกฤษ": [story_english]})
            story_csv = data.to_csv(index=False).encode("utf-8")
            vocab_csv = vocab_df.to_csv(index=False).encode("utf-8")
            st.download_button("ดาวน์โหลดผลลัพธ์นิทาน (CSV)", data=story_csv, file_name="story.csv", mime="text/csv")
            st.download_button("ดาวน์โหลดคำศัพท์ (CSV)", data=vocab_csv, file_name="vocabulary.csv", mime="text/csv")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")




