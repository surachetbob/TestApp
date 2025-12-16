import streamlit as st

# 1. ส่วนหัวของเว็บ
st.title("เครื่องคำนวณอัจฉริยะ")
st.subheader("กรอกข้อมูลเพื่อหาผลลัพธ์")

# 2. ส่วนรับข้อมูล (Input)
number = st.number_input("ใส่ตัวเลขที่ต้องการคำนวณ", value=0)
multiplier = st.slider("เลือกตัวคูณ", 1, 10, 1)

# 3. ส่วนเงื่อนไขและการคำนวณ (Logic)
result = number * multiplier

if result > 100:
    message = "ผลลัพธ์สูงเกินไป!"
else:
    message = "ผลลัพธ์อยู่ในเกณฑ์ปกติ"

# 4. ส่วนแสดงผล (Output)
st.write("---")
st.write(f"### ผลคำนวณคือ: {result}")
st.info(f"สถานะ: {message}")