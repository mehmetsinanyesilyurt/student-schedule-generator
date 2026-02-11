import streamlit as st
import pandas as pd
from datetime import datetime, time

# --- SAYFA AYARLARI (Midas Temizliği) ---
st.set_page_config(page_title="Ders Planlayıcı", layout="wide", initial_sidebar_state="expanded")

# --- ÖZEL CSS (Beyaz, Ferah Tasarım) ---
st.markdown("""
<style>
    /* Ana Arka Plan Beyaz */
    .stApp { background-color: #FFFFFF; color: #1e293b; }
    
    /* Sidebar (Sol Panel) Hafif Gri */
    section[data-testid="stSidebar"] { background-color: #F8FAFC; border-right: 1px solid #E2E8F0; }
    
    /* Butonlar Midas Siyahı */
    .stButton button { 
        background-color: #0F172A; 
        color: white; 
        border-radius: 8px; 
        border: none; 
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton button:hover { background-color: #334155; color: white; }
    
    /* Tablo Başlıkları */
    thead tr th:first-child { display:none }
    tbody th { display:none }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE (Verileri Hafızada Tut) ---
if 'schedule' not in st.session_state:
    st.session_state.schedule = []

# --- FONKSİYONLAR ---
def check_conflict(day, start_t, end_t):
    """Çakışma var mı kontrol eder"""
    for item in st.session_state.schedule:
        if item['day'] == day:
            # (Yeni Başlangıç < Eski Bitiş) VE (Yeni Bitiş > Eski Başlangıç)
            if (start_t < item['end']) and (end_t > item['start']):
                return True, item['course']
    return False, None

def create_schedule_dataframe():
    """Listeyi Haftalık Tabloya Çevirir"""
    days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
    # 08:00 - 20:00 arası saat dilimleri
    hours = [f"{h:02d}:00" for h in range(8, 21)] 
    
    # Boş bir DataFrame oluştur
    df = pd.DataFrame("", index=hours, columns=days)
    
    for item in st.session_state.schedule:
        day_name = item['day']
        start_hour = item['start'].hour
        end_hour = item['end'].hour
        course_name = item['course']
        
        # O saat aralığındaki hücreleri doldur
        for h in range(start_hour, end_hour):
            if 8 <= h <= 20:
                time_str = f"{h:02d}:00"
                current_val = df.at[time_str, day_name]
                # Eğer hücre boşsa yaz, doluysa yanına ekle (nadir durum)
                df.at[time_str, day_name] = course_name if current_val == "" else f"{current_val}\n{course_name}"
    
    return df

# --- ARAYÜZ (SIDEBAR) ---
with st.sidebar:
    st.title("Planlayıcı")
    st.caption("Ders programını oluştur.")
    
    with st.form("add_course_form", clear_on_submit=True):
        course_name = st.text_input("Ders Adı", placeholder="Örn: Veri Tabanı")
        
        day = st.selectbox("Gün", ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"])
        
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("Başlangıç", value=time(9, 0))
        with col2:
            end_time = st.time_input("Bitiş", value=time(11, 0))
            
        submitted = st.form_submit_button("Ders Ekle")
        
        if submitted:
            if start_time >= end_time:
                st.error("Bitiş saati başlangıçtan önce olamaz!")
            else:
                conflict, conflicting_course = check_conflict(day, start_time, end_time)
                if conflict:
                    st.error(f"Çakışma Var: {conflicting_course}")
                else:
                    st.session_state.schedule.append({
                        "course": course_name,
                        "day": day,
                        "start": start_time,
                        "end": end_time
                    })
                    st.success(f"{course_name} eklendi.")

    if st.button("Tüm Programı Temizle"):
        st.session_state.schedule = []
        st.rerun()

# --- ARAYÜZ (ANA EKRAN) ---
st.header("Haftalık Ders Programı")

if not st.session_state.schedule:
    st.info("Henüz ders eklemediniz. Sol taraftan ders ekleyin.")
else:
    # Programı DataFrame olarak hazırla
    schedule_df = create_schedule_dataframe()
    
    # Tabloyu Renklendir ve Göster
    def color_schedule(val):
        """Ders varsa hücreyi Mavi yap"""
        if val != "":
            return 'background-color: #EFF6FF; color: #1e3a8a; border-radius: 4px; font-weight: bold;'
        return ''

    st.dataframe(
        schedule_df.style.map(color_schedule),
        use_container_width=True,
        height=600
    )
