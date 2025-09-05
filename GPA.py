import streamlit as st
import json

# Harf notlarının katsayıları
grade_points = {
    "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0,
    "D-": 0.7, "F": 0.0, "P": 0.0
}

# Yarıyıllara göre dersler (stajlar kaldırıldı)
predefined_courses = {
    "1. Yarıyıl": [
        {"name": "PHYSICS I", "credit": 7},
        {"name": "CALCULUS I", "credit": 7},
        {"name": "LINEAR ALGEBRA", "credit": 6},
        {"name": "ACADEMIC ENGLISH", "credit": 3},
        {"name": "PROGRAMMING FOR ENGINEERS", "credit": 6},
        {"name": "PRINCIPLES OF ATATÜRK & HISTORY OF REFOR", "credit": 2},
        {"name": "TURKISH I", "credit": 2},
    ],
    "2. Yarıyıl": [
        {"name": "CALCULUS II", "credit": 7},
        {"name": "DIFFERENTIAL EQUATIONS", "credit": 6},
        {"name": "ACADEMIC ENGLISH", "credit": 3},
        {"name": "INTRODUCTION TO ELECTRIC CIRCUITS", "credit": 6},
        {"name": "CHEMISTRY", "credit": 6},
        {"name": "TURKISH II", "credit": 2},
        {"name": "PRINCIPLES OF ATATÜRK", "credit": 2},
        {"name": "ELECTRIC CIRCUITS LABORATORY", "credit": 3},
    ],
    "3. Yarıyıl": [
        {"name": "LOGIC CIRCUITS LABORATORY", "credit": 3},
        {"name": "INTRODUCTION TO ELECTROMAGNETICS", "credit": 5},
        {"name": "NUMERICAL METHODS", "credit": 6},
        {"name": "CIRCUIT ANALYSIS", "credit": 6},
        {"name": "LOGIC DESIGN", "credit": 6},
        {"name": "SIGNALS AND SYSTEMS", "credit": 6},
    ],
    "4. Yarıyıl": [
        {"name": "ELECTRONIC CIRCUITS I", "credit": 6},
        {"name": "ELECTRONIC CIRCUITS I LABORATORY", "credit": 3},
        {"name": "INTRODUCTION TO TELECOMMUNICATION", "credit": 6},
        {"name": "INTRODUCTION TO RANDOM SIGNALS", "credit": 5},
        {"name": "TELECOMMUNICATION LABORATORY", "credit": 3},
        {"name": "ELECTROMAGNETIC FIELD THEORY", "credit": 6},
    ],
    "5. Yarıyıl": [
        {"name": "ELECTRONIC CIRCUITS II LABORATORY", "credit": 3},
        {"name": "ELECTRONIC CIRCUITS I", "credit": 6},
        {"name": "MICROPROCESSORS", "credit": 5},
        {"name": "DIGITAL SIGNAL PROCESSING", "credit": 6},
        {"name": "INTRODUCTION TO CONTROL SYSTEMS", "credit": 5},
    ],
    "6. Yarıyıl": [
        {"name": "TECHNICAL WRITING AND PRESENTATION", "credit": 4},
        {"name": "MATERIALS SCIENCE", "credit": 3},
        {"name": "ELECTROMECHANICAL ENERGY CONVERSION", "credit": 5},
    ],
    "7. Yarıyıl": [
        {"name": "ENGINEERING ORIENTATION", "credit": 2},
        {"name": "ELECTROMECHANICAL ENERGY CONVERSION", "credit": 5},
    ],
    "8. Yarıyıl": [
        {"name": "GRADUATION PROJECT", "credit": 12},
    ],
}

# GPA hesaplama
def calculate_gpa(courses):
    gpa_points, gpa_credits = 0, 0
    valid_credits, invalid_credits = 0, 0

    for course in courses:
        grade = course.get("grade")
        credit = course["credit"]

        if grade is None:
            continue

        gpa_points += grade_points[grade] * credit
        gpa_credits += credit

        if grade == "F":
            invalid_credits += credit
        else:
            valid_credits += credit

    gpa = gpa_points / gpa_credits if gpa_credits > 0 else 0
    return gpa, valid_credits, invalid_credits, gpa_credits


# --- Streamlit Arayüzü ---
st.title("🎓 GPA Hesaplama Uygulaması")

# Staj Seçenekleri
st.sidebar.header("Stajlar")
staj1 = st.sidebar.checkbox("INDUSTRY TRAINING I (3 kredi)")
staj2 = st.sidebar.checkbox("INDUSTRY TRAINING II (3 kredi)")

staj_credits = 0
if staj1:
    staj_credits += 3
if staj2:
    staj_credits += 3

# Yarıyıl seçimi
semester = st.sidebar.selectbox("Yarıyıl Seç", list(predefined_courses.keys()))

# Session state hazırlığı
if "courses" not in st.session_state:
    st.session_state["courses"] = {}

# Ders listesi göster ve not seçtir
st.subheader(f"📚 {semester} Dersleri")

entered_courses = st.session_state["courses"].get(semester, [])

# Ön tanımlı dersler
for course in predefined_courses[semester]:
    grade = st.selectbox(
        f"{course['name']} ({course['credit']} kredi)",
        list(grade_points.keys()),
        key=f"{semester}-{course['name']}",
        index=list(grade_points.keys()).index(
            next((c["grade"] for c in entered_courses if c["name"] == course["name"]), "A")
        ) if entered_courses else 0
    )
    new_course = {
        "name": course["name"],
        "credit": course["credit"],
        "grade": grade,
        "type": "normal"
    }
    entered_courses = [c for c in entered_courses if c["name"] != course["name"]] + [new_course]

# Seçmeli ders ekleme
with st.expander("➕ Seçmeli Ders Ekle"):
    elective_name = st.text_input("Seçmeli Ders Adı", key=f"elective-{semester}")
    elective_grade = st.selectbox("Seçmeli Ders Notu", list(grade_points.keys()), key=f"elective-grade-{semester}")
    if st.button("Ekle", key=f"add-elective-{semester}") and elective_name:
        entered_courses.append({"name": elective_name, "credit": 6, "grade": elective_grade, "type": "elective"})

# Kaydet
if st.button("💾 Kaydet"):
    st.session_state["courses"][semester] = entered_courses

# Kayıtlı seçmeli dersleri göster
if any(c["type"] == "elective" for c in entered_courses):
    st.write("📌 Eklenen Seçmeli Dersler:")
    for c in [c for c in entered_courses if c["type"] == "elective"]:
        st.write(f"- {c['name']} ({c['credit']} kredi) | Not: {c['grade']}")

# --- JSON Kaydet / Yükle ---
st.markdown("---")
st.subheader("💽 Verileri Kaydet / Yükle")

# JSON indir
data = json.dumps(st.session_state["courses"], ensure_ascii=False, indent=2)
st.download_button(
    label="📥 JSON Olarak İndir",
    data=data,
    file_name="gpa_data.json",
    mime="application/json"
)

# JSON yükle
uploaded_file = st.file_uploader("📂 Daha önce kaydedilmiş veriyi yükle", type="json")
if uploaded_file is not None:
    st.session_state["courses"] = json.load(uploaded_file)
    st.success("✅ Veriler başarıyla yüklendi!")

# --- Hesaplama ---
if st.session_state["courses"]:
    # Dönem bazlı
    for sem_key, courses in st.session_state["courses"].items():
        st.subheader(f"📊 {sem_key} Sonuçları")
        gpa, valid, invalid, total_gpa = calculate_gpa(courses)
        st.write(f"**GPA:** {gpa:.2f}")
        st.write(f"Stajlar Hariç TOPLAM KREDİ: {valid}")
        st.write(f"Stajlar Dahil TOPLAM KREDİ: {valid + staj_credits}")
        if invalid > 0:
            st.write(f"Geçersiz Kredi (F Notu): {invalid}")
        st.markdown("---")

    # Genel sonuç
    all_courses = [c for sem in st.session_state["courses"].values() for c in sem]
    gpa, valid, invalid, total_gpa = calculate_gpa(all_courses)
    st.subheader("📈 Genel Sonuç")
    st.write(f"**Genel GPA:** {gpa:.2f}")
    st.write(f"Stajlar Hariç TOPLAM KREDİ: {valid}")
    st.write(f"Stajlar Dahil TOPLAM KREDİ: {valid + staj_credits}")
    if invalid > 0:
        st.write(f"Geçersiz Kredi (F Notu): {invalid}")
