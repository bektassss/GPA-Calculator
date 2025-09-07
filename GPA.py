import streamlit as st
import json
import uuid

# --- Harf notlarının katsayıları ---
grade_points = {
    "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0,
    "D-": 0.7, "F": 0.0, "P": 0.0,
    "Alınmadı": None
}
grades = list(grade_points.keys())

# --- GPA hesaplama ---
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

# --- Varsayılan dersler ---
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

# --- Session başlat ---
if "courses" not in st.session_state:
    st.session_state["courses"] = {
        sem: [
            {"name": c["name"], "credit": c["credit"], "grade": "Alınmadı", "type": "normal", "id": c["name"]}
            for c in lst
        ]
        for sem, lst in predefined_courses.items()
    }

# --- JSON yükleme (sadece ilk defa) ---
uploaded_file = st.sidebar.file_uploader("📂 JSON yükle", type="json")
if uploaded_file is not None and "loaded" not in st.session_state:
    st.session_state["courses"] = json.load(uploaded_file)
    st.session_state["loaded"] = True
    st.sidebar.success("✅ JSON yüklendi!")

# --- Staj Seçenekleri ---
st.sidebar.header("🛠️ Stajlar")
staj1 = st.sidebar.checkbox("INDUSTRY TRAINING I (3 kredi)")
staj2 = st.sidebar.checkbox("INDUSTRY TRAINING II (3 kredi)")
staj_credits = (3 if staj1 else 0) + (3 if staj2 else 0)

# --- Seçmeli ekleme ---
st.sidebar.header("➕ Seçmeli Ders Ekle")
target_semester = st.sidebar.selectbox("Yarıyıl Seç", list(predefined_courses.keys()))
elective_name = st.sidebar.text_input("Ders Adı")
elective_credit = st.sidebar.number_input("Kredi", min_value=1, max_value=20, value=6)
elective_grade = st.sidebar.selectbox("Not", grades, key="elective-grade")

if st.sidebar.button("Ekle"):
    st.session_state["courses"][target_semester].append({
        "name": elective_name,
        "credit": elective_credit,
        "grade": elective_grade,
        "type": "elective",
        "id": str(uuid.uuid4())
    })
    st.sidebar.success(f"{target_semester} için '{elective_name}' eklendi!")

# --- Dersleri Göster ---
for semester, courses in st.session_state["courses"].items():
    st.subheader(f"📚 {semester} Dersleri")
    for course in courses:
        key = f"{semester}-{course['id']}"
        current_grade = course["grade"]
        selected = st.selectbox(
            f"{course['name']} ({course['credit']} kredi)",
            grades,
            index=grades.index(current_grade),
            key=key
        )
        if course["grade"] != selected:
            course["grade"] = selected
    st.markdown("---")

# --- JSON Kaydet ---
data = json.dumps(st.session_state["courses"], ensure_ascii=False, indent=2)
st.download_button("📥 JSON Olarak İndir", data=data, file_name="gpa_data.json", mime="application/json")

# --- Genel Sonuç ---
all_courses = [c for sem in st.session_state["courses"].values() for c in sem]
gpa, valid, invalid, total_gpa, not_taken = calculate_gpa(all_courses)

st.subheader("📈 Genel Sonuç")
st.write(f"**Genel GPA:** {gpa:.2f}")
st.write(f"TOPLAM KREDİ (stajlar hariç): {valid}")
st.write(f"TOPLAM KREDİ (stajlar dahil): {valid + staj_credits}")
if invalid > 0:
    st.write(f"Geçersiz Kredi (F Notu): {invalid}")
if not_taken:
    for ders in not_taken:
        st.write(f"❌ **{ders}** dersi alınmadı.")

# --- Sidebar GPA hızlı görünüm ---
st.sidebar.header("📊 GPA Görüntüle")
gpa_option = st.sidebar.selectbox("Seçiniz", ["Genel GPA", "Stajlar Hariç"])
if gpa_option == "Genel GPA":
    st.sidebar.success(f"Genel GPA: {gpa:.2f} | Krediler: {valid + staj_credits}")
else:
    st.sidebar.success(f"Stajlar Hariç GPA: {gpa:.2f} | Krediler: {valid}")
