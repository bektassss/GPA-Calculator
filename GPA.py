import streamlit as st
import json

# Harf notlarının katsayıları
grade_points = {
    "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0,
    "D-": 0.7, "F": 0.0, "P": 0.0,
    "Alınmadı": None
}

# GPA hesaplama
def calculate_gpa(courses):
    gpa_points, gpa_credits = 0, 0
    valid_credits, invalid_credits = 0, 0
    not_taken = []

    for course in courses:
        grade = course.get("grade")
        credit = course["credit"]

        if grade == "Alınmadı":
            not_taken.append(course["name"])
            continue

        if grade is None:
            continue

        gpa_points += grade_points[grade] * credit
        gpa_credits += credit

        if grade == "F":
            invalid_credits += credit
        else:
            valid_credits += credit

    gpa = gpa_points / gpa_credits if gpa_credits > 0 else 0
    return gpa, valid_credits, invalid_credits, gpa_credits, not_taken


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
semester = st.sidebar.selectbox("Yarıyıl Seç", [
    "1. Yarıyıl","2. Yarıyıl","3. Yarıyıl","4. Yarıyıl",
    "5. Yarıyıl","6. Yarıyıl","7. Yarıyıl","8. Yarıyıl"
])

# Session state hazırlığı
if "courses" not in st.session_state:
    st.session_state["courses"] = {}

if semester not in st.session_state["courses"]:
    st.session_state["courses"][semester] = []

entered_courses = st.session_state["courses"][semester]

# Zorunlu dersler listesi
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

st.subheader(f"📚 {semester} Dersleri")

# Ön tanımlı dersler
for course in predefined_courses.get(semester, []):
    prev = next((c for c in entered_courses if c["name"] == course["name"]), None)
    grade = st.selectbox(
        f"{course['name']} ({course['credit']} kredi)",
        list(grade_points.keys()),
        key=f"{semester}-{course['name']}",
        index=list(grade_points.keys()).index(prev["grade"]) if prev else list(grade_points.keys()).index("Alınmadı")
    )
    new_course = {"name": course["name"], "credit": course["credit"], "grade": grade, "type": "normal"}
    entered_courses = [c for c in entered_courses if c["name"] != course["name"]] + [new_course]

# Seçmeli ders ekleme
with st.expander("➕ Seçmeli Ders Ekle"):
    elective_name = st.text_input("Seçmeli Ders Adı", key=f"elective-{semester}")
    elective_credit = st.number_input("Kredi", min_value=1, max_value=20, value=6, key=f"elective-credit-{semester}")
    elective_grade = st.selectbox("Seçmeli Ders Notu", list(grade_points.keys()), key=f"elective-grade-{semester}")
    if st.button("Ekle", key=f"add-elective-{semester}") and elective_name:
        entered_courses.append({
            "name": elective_name,
            "credit": elective_credit,
            "grade": elective_grade,
            "type": "elective"
        })

# Seçmeli dersleri düzenleme
if any(c["type"] == "elective" for c in entered_courses):
    st.write("📌 Eklenen Seçmeli Dersler:")
    new_list = []
    for i, c in enumerate([c for c in entered_courses if c["type"] == "elective"]):
        grade = st.selectbox(
            f"{c['name']} ({c['credit']} kredi)",
            list(grade_points.keys()),
            key=f"{semester}-elective-{i}",
            index=list(grade_points.keys()).index(c["grade"])
        )
        new_list.append({"name": c["name"], "credit": c["credit"], "grade": grade, "type": "elective"})
    # Güncelle elective dersler
    entered_courses = [c for c in entered_courses if c["type"] != "elective"] + new_list

# Kaydet
if st.button("💾 Kaydet"):
    st.session_state["courses"][semester] = entered_courses

# --- JSON Kaydet / Yükle ---
st.markdown("---")
st.subheader("💽 Verileri Kaydet / Yükle")

# JSON indir
data = json.dumps(st.session_state["courses"], ensure_ascii=False, indent=2)
st.download_button("📥 JSON Olarak İndir", data=data, file_name="gpa_data.json", mime="application/json")

# JSON yükle
uploaded_file = st.file_uploader("📂 Daha önce kaydedilmiş veriyi yükle", type="json")
if uploaded_file is not None:
    st.session_state["courses"] = json.load(uploaded_file)
    st.success("✅ Veriler başarıyla yüklendi!")

# --- Hesaplama ---
if st.session_state["courses"]:
    for sem_key, courses in st.session_state["courses"].items():
        st.subheader(f"📊 {sem_key} Sonuçları")
        gpa, valid, invalid, total_gpa, not_taken = calculate_gpa(courses)
        st.write(f"**GPA:** {gpa:.2f}")
        st.write(f"Stajlar Hariç TOPLAM KREDİ: {valid}")
        st.write(f"Stajlar Dahil TOPLAM KREDİ: {valid + staj_credits}")
        if invalid > 0:
            st.write(f"Geçersiz Kredi (F Notu): {invalid}")
        if not_taken:
            for ders in not_taken:
                st.write(f"❌ Bu yarıyılda **{ders}** dersi alınmadı.")
        st.markdown("---")

    all_courses = [c for sem in st.session_state["courses"].values() for c in sem]
    gpa, valid, invalid, total_gpa, not_taken = calculate_gpa(all_courses)
    st.subheader("📈 Genel Sonuç")
    st.write(f"**Genel GPA:** {gpa:.2f}")
    st.write(f"Stajlar Hariç TOPLAM KREDİ: {valid}")
    st.write(f"Stajlar Dahil TOPLAM KREDİ: {valid + staj_credits}")
    if invalid > 0:
        st.write(f"Geçersiz Kredi (F Notu): {invalid}")
    if not_taken:
        for ders in not_taken:
            st.write(f"❌ Bu yarıyılda **{ders}** dersi alınmadı.")
