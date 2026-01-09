import streamlit as st
import json
import uuid

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="GPA Hesaplayıcı", layout="wide", page_icon="🎓")

# --- SABİTLER ---
GRADE_SCALE = {
    "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0,
    "D-": 0.7, "F": 0.0, 
    "Alınmadı": None
}
GRADE_OPTIONS = list(GRADE_SCALE.keys())

# Varsayılan ders yapıları (Senin listen)
PREDEFINED_COURSES = {
    "1. Yarıyıl": [
        {"name": "PHYSICS I", "credit": 7}, {"name": "CALCULUS I", "credit": 7},
        {"name": "LINEAR ALGEBRA", "credit": 6}, {"name": "ACADEMIC ENGLISH", "credit": 3},
        {"name": "PROGRAMMING FOR ENGINEERS", "credit": 6}, {"name": "PRINCIPLES OF ATATÜRK & HISTORY OF REFOR", "credit": 2},
        {"name": "TURKISH I", "credit": 2}
    ],
    "2. Yarıyıl": [
        {"name": "CALCULUS II", "credit": 7}, {"name": "DIFFERENTIAL EQUATIONS", "credit": 6},
        {"name": "ACADEMIC ENGLISH", "credit": 3}, {"name": "INTRODUCTION TO ELECTRIC CIRCUITS", "credit": 6},
        {"name": "CHEMISTRY", "credit": 6}, {"name": "TURKISH II", "credit": 2},
        {"name": "PRINCIPLES OF ATATÜRK", "credit": 2}, {"name": "ELECTRIC CIRCUITS LABORATORY", "credit": 3}
    ],
    "3. Yarıyıl": [
        {"name": "LOGIC CIRCUITS LABORATORY", "credit": 3}, {"name": "INTRODUCTION TO ELECTROMAGNETICS", "credit": 5},
        {"name": "NUMERICAL METHODS", "credit": 6}, {"name": "CIRCUIT ANALYSIS", "credit": 6},
        {"name": "LOGIC DESIGN", "credit": 6}, {"name": "SIGNALS AND SYSTEMS", "credit": 6}
    ],
    "4. Yarıyıl": [
        {"name": "ELECTRONIC CIRCUITS I", "credit": 6}, {"name": "ELECTRONIC CIRCUITS I LABORATORY", "credit": 3},
        {"name": "INTRODUCTION TO TELECOMMUNICATION", "credit": 6}, {"name": "INTRODUCTION TO RANDOM SIGNALS", "credit": 5},
        {"name": "TELECOMMUNICATION LABORATORY", "credit": 3}, {"name": "ELECTROMAGNETIC FIELD THEORY", "credit": 6}
    ],
    "5. Yarıyıl": [
        {"name": "ELECTRONIC CIRCUITS II LABORATORY", "credit": 3}, {"name": "ELECTRONIC CIRCUITS II", "credit": 5},
        {"name": "MICROPROCESSORS", "credit": 5}, {"name": "DIGITAL SIGNAL PROCESSING", "credit": 6},
        {"name": "INTRODUCTION TO CONTROL SYSTEMS", "credit": 5}, {"name": "MODERN PHYSICS", "credit": 2, "type": "elective"},
        {"name": "EARTHQUAKE AWARENESS", "credit": 2, "type": "elective"}
    ],
    "6. Yarıyıl": [
        {"name": "TECHNICAL WRITING AND PRESENTATION", "credit": 4}, {"name": "MATERIALS SCIENCE", "credit": 3},
        {"name": "ELECTROMECHANICAL ENERGY CONVERSION", "credit": 5}
    ],
    "7. Yarıyıl": [
        {"name": "ENGINEERING ORIENTATION", "credit": 2}
    ],
    "8. Yarıyıl": [
        {"name": "GRADUATION PROJECT", "credit": 12}
    ]
}

# --- FONKSİYONLAR ---

def init_session():
    """Session state başlatır veya sıfırlar."""
    if "courses" not in st.session_state:
        st.session_state["courses"] = {}
        for sem, course_list in PREDEFINED_COURSES.items():
            st.session_state["courses"][sem] = []
            for c in course_list:
                # UUID ekleyerek her derse benzersiz bir kimlik veriyoruz
                st.session_state["courses"][sem].append({
                    "name": c["name"],
                    "credit": c["credit"],
                    "grade": "Alınmadı",
                    "type": c.get("type", "normal"),
                    "id": str(uuid.uuid4())
                })
    
    if "file_processed" not in st.session_state:
        st.session_state["file_processed"] = False

def calculate_gpa(courses_dict):
    """AGNO hesaplar."""
    total_points = 0
    total_credits_gpa = 0  # Ortalamaya katılan kredi
    total_credits_earned = 0 # Kazanılan toplam kredi (F dahil değil)
    
    flat_list = []
    for sem in courses_dict.values():
        flat_list.extend(sem)

    for course in flat_list:
        grade = course.get("grade")
        credit = course.get("credit", 0)
        
        if grade == "Alınmadı" or grade is None:
            continue
            
        points = GRADE_SCALE.get(grade)
        
        if points is not None:
            # Ortalamaya katılanlar
            total_points += points * credit
            total_credits_gpa += credit
            
            # Krediyi kazanma durumu (F değilse)
            if grade != "F":
                total_credits_earned += credit

    gpa = total_points / total_credits_gpa if total_credits_gpa > 0 else 0.0
    return gpa, total_credits_earned, total_credits_gpa

# --- ANA UYGULAMA ---

init_session()

# --- SIDEBAR: YÜKLEME VE AYARLAR ---
st.sidebar.title("⚙️ İşlemler")

# 1. JSON Yükleme (Düzeltilen Kısım)
uploaded_file = st.sidebar.file_uploader("📂 JSON Dosyası Yükle", type="json")

if uploaded_file is not None:
    # Dosya yüklendi ama henüz işlenmediyse veya yeni bir dosya ise
    if not st.session_state["file_processed"]:
        try:
            data = json.load(uploaded_file)
            st.session_state["courses"] = data
            st.session_state["file_processed"] = True
            st.sidebar.success("✅ Veriler yüklendi!")
            st.rerun() # EKRANI YENİLEMEK İÇİN KRİTİK KOMUT
        except Exception as e:
            st.sidebar.error(f"Dosya okunamadı: {e}")
elif st.session_state["file_processed"]:
    # Dosya kaldırılırsa flag'i sıfırla
    st.session_state["file_processed"] = False

st.sidebar.markdown("---")

# 2. Seçmeli Ders Ekleme
st.sidebar.header("➕ Ders Ekle")
with st.sidebar.form("add_course_form"):
    sem_select = st.selectbox("Dönem", list(PREDEFINED_COURSES.keys()))
    new_name = st.text_input("Ders Adı")
    new_credit = st.number_input("Kredi", min_value=1, value=5)
    new_grade = st.selectbox("Not", GRADE_OPTIONS)
    submitted = st.form_submit_button("Ekle")
    
    if submitted and new_name:
        st.session_state["courses"][sem_select].append({
            "name": new_name,
            "credit": new_credit,
            "grade": new_grade,
            "type": "elective",
            "id": str(uuid.uuid4())
        })
        st.success(f"{new_name} eklendi!")
        st.rerun()

# --- ANA EKRAN: DERS LİSTESİ ---
st.title("🎓 Not Ortalaması Hesaplayıcı")

# İki sütun: Sol taraf dersler, Sağ taraf özet
col_main, col_summary = st.columns([3, 1])

with col_main:
    st.write("Ders notlarını aşağıdan güncelleyebilirsiniz. Değişiklikler anında hesaplanır.")
    
    # Dönemleri Expander (Açılır Kutu) içinde göstermek daha temiz bir görüntü sağlar
    for semester, courses in st.session_state["courses"].items():
        # O dönemin ortalamasını hesapla (Başlıkta göstermek için)
        sem_gpa, _, sem_cr = calculate_gpa({semester: courses})
        header_text = f"{semester}"
        if sem_cr > 0:
            header_text += f" (Dönem Ort: {sem_gpa:.2f})"
            
        with st.expander(header_text, expanded=False):
            # Dersleri 3 sütun halinde gösterelim
            cols = st.columns(3)
            for i, course in enumerate(courses):
                col = cols[i % 3]
                
                # Unique Key oluşturma
                widget_key = f"{semester}_{course['id']}"
                
                # Mevcut notu index olarak bul
                try:
                    current_idx = GRADE_OPTIONS.index(course["grade"])
                except ValueError:
                    current_idx = GRADE_OPTIONS.index("Alınmadı")
                
                new_grade = col.selectbox(
                    f"{course['name']} ({course['credit']} Kr)",
                    options=GRADE_OPTIONS,
                    index=current_idx,
                    key=widget_key
                )
                
                # State güncelleme
                if new_grade != course["grade"]:
                    course["grade"] = new_grade
                    st.rerun()

    # JSON İndirme Butonu (En altta)
    st.markdown("---")
    json_data = json.dumps(st.session_state["courses"], ensure_ascii=False, indent=2)
    st.download_button(
        label="💾 Verileri JSON Olarak İndir",
        data=json_data,
        file_name="notlarim.json",
        mime="application/json"
    )

# --- SAĞ SÜTUN: CANLI ÖZET ---
with col_summary:
    st.markdown("### 📊 Genel Durum")
    
    gpa, earned_credits, gpa_credits = calculate_gpa(st.session_state["courses"])
    
    # Metrik gösterimi (Daha şık)
    st.metric(label="Genel Ortalam (AGNO)", value=f"{gpa:.2f}")
    
    st.markdown("---")
    st.write(f"**Tamamlanan Kredi:** {earned_credits}")
    st.write(f"**GPA'ya Giren Kredi:** {gpa_credits}")
    
    # Kalan Kredi Tahmini (Örnek: Mezuniyet için 240 kredi varsayalım)
    target_credit = 240
    progress = min(earned_credits / target_credit, 1.0)
    st.progress(progress)
    st.caption(f"Mezuniyet İlerlemesi: %{int(progress*100)}")

    # Staj Ekleme (Manuel)
    st.markdown("### 🏭 Stajlar")
    staj1 = st.checkbox("Staj I (3 Kredi)", value=False)
    staj2 = st.checkbox("Staj II (3 Kredi)", value=False)
    
    total_with_internship = earned_credits + (3 if staj1 else 0) + (3 if staj2 else 0)
    st.info(f"Staj Dahil Toplam: **{total_with_internship}**")
