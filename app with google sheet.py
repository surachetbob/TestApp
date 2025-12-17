import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. ตั้งค่า Layout
st.set_page_config(page_title="PA Insurance Calculator", layout="centered")

# เชื่อมต่อ Google Sheets (ต้องตั้งค่า URL ใน .streamlit/secrets.toml หรือใส่ตรงๆ เพื่อทดสอบ)
# สำหรับการใช้งานจริงแนะนำให้ใส่ใน Secrets ของ Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

# CSS สำหรับ UI
st.markdown("""
    <style>
    div.stButton > button:first-child {
        width: 100%;
        height: 50px;
        font-size: 20px;
        border-radius: 10px;
        background-color: #ff4b4b;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

PLAN_BENEFITS = {
    "AIANPA2500": {
        "เสียชีวิต/ทุพพลภาพ (AD,DD,PD)": "500,000",
        "ค่ารักษาพยาบาล (ME)": "20,000",
        "ช่วงอายุที่รับประกัน": "15 วัน - 70 ปี"
    },
    "AIANPA3000": {
        "เสียชีวิต/ทุพพลภาพ (AD,DD,PD)": "600,000",
        "ค่ารักษาพยาบาล (ME)": "35,000",
        "ช่วงอายุที่รับประกัน": "15 วัน - 74 ปี"
    },
    "AIANPA3800": {
        "เสียชีวิต/ทุพพลภาพ (AD,DD,PD)": "500,000",
        "ค่ารักษาพยาบาล (ME)": "50,000",
        "ช่วงอายุที่รับประกัน": "16 - 60 ปี"
    }
}

def get_premium(plan, age):
    if plan == "AIANPA2500":
        if age <= 60: return 2500
        elif age <= 65: return 2700
        elif age <= 70: return 3150
        elif age <= 75: return 4000
    elif plan == "AIANPA3000":
        if age <= 60: return 3000
        elif age <= 65: return 3250
        elif age <= 70: return 3750
        elif age <= 75: return 4700
    elif plan == "AIANPA3800":
        if age <= 60: return 3800
        elif age <= 65: return 4600
        elif age <= 70: return 5300
        elif age <= 75: return 6770
    return 0

# --- UI หลัก ---
st.title("🛡️ เช็คเบี้ยและความคุ้มครอง")

with st.expander("👤 กรอกข้อมูลผู้ขอเอาประกัน", expanded=True):
    name = st.text_input("ชื่อ-นามสกุล")
    phone = st.text_input("เบอร์โทรศัพท์", max_chars=10, help="กรอกเฉพาะตัวเลข 10 หลัก")
    
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("อายุ (ปี)", min_value=0, max_value=75, value=25)
    with c2:
        gender = st.selectbox("เพศ", ["ชาย", "หญิง"])
        
    plan_choice = st.selectbox("เลือกแผนประกันภัย", list(PLAN_BENEFITS.keys()))
    submit = st.button("🚀 คำนวณเบี้ยและบันทึกข้อมูล")

if submit:
    if not name or not phone:
        st.warning("⚠️ กรุณากรอกชื่อและเบอร์โทรศัพท์ให้ครบถ้วน")
    else:
        premium = get_premium(plan_choice, age)
        
        # --- บันทึกข้อมูลลง Google Sheet ---
        try:
            # ดึงข้อมูลเดิมที่มีอยู่
            existing_data = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"])
            
            # เตรียมข้อมูลใหม่
            new_data = pd.DataFrame([{
                "name": name,
                "phone": f"'{phone}", # ใส่ ' นำหน้าเพื่อให้ Excel/Sheet ไม่ตัดเลข 0 ตัวแรก
                "age": age,
                "gender": gender,
                "plan": plan_choice,
                "premium": premium,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            
            # รวมข้อมูลและอัปเดต
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=updated_df)
            
            st.success("✅ บันทึกข้อมูลสนใจเรียบร้อยแล้ว!")
        except Exception as e:
            st.error(f"ไม่สามารถบันทึกข้อมูลได้: {e}")

        # --- แสดงผล UI ---
        st.divider()
        st.balloons()
        st.markdown(f"""
            <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; text-align:center;">
                <h3 style="margin:0;">เบี้ยประกันภัยรายปี</h3>
                <h1 style="color:#ff4b4b; margin:0;">{premium:,} บาท</h1>
            </div>
        """, unsafe_allow_html=True)

        st.subheader(f"📋 ความคุ้มครอง {plan_choice}")
        benefits = PLAN_BENEFITS[plan_choice]
        benefit_data = [{"รายการ": k, "วงเงิน (บาท)": v} for k, v in benefits.items()]
        st.dataframe(benefit_data, use_container_width=True, hide_index=True)

        st.info("📞 **เจ้าหน้าที่จะติดต่อกลับที่เบอร์:** " + phone)
