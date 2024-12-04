import streamlit as st
import openai

st.sidebar.title("NLP Story Generator")
api_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password")
if api_key:
    openai.api_key = api_key

st.title("10-Line Story Generator")
st.write("กรอกคีย์เวิร์ดเพื่อสร้างนิทาน 10 บรรทัด")

keywords = st.text_input("คีย์เวิร์ด (เช่น มังกร, เจ้าหญิง, ภูเขาไฟ):")
style = st.selectbox("เลือกสไตล์ของนิทาน", ["ตลก", "ดราม่า", "ผจญภัย"])

if st.button("สร้างนิทาน"):
    if not keywords:
        st.error("กรุณากรอกคีย์เวิร์ด")
    elif not api_key:
        st.error("กรุณากรอก API Key ใน Sidebar")
    else:
        thai_prompt = f"เขียนนิทาน 10 บรรทัดโดยใช้คำต่อไปนี้: {keywords} และให้มีสไตล์ {style}"
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # ใช้ gpt-3.5-turbo หรือ gpt-4
                messages=[
                    {"role": "system", "content": "คุณเป็นนักเขียนนิทาน"},
                    {"role": "user", "content": thai_prompt}
                ]
            )
            story_thai = response["choices"][0]["message"]["content"]
            st.subheader("นิทานภาษาไทย")
            st.write(story_thai)
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

