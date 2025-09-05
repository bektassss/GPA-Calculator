import streamlit as st

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

# Staj Seçenekleri (sadece krediye etki eder)
st.sidebar.header("Stajlar")
staj1 = st.sidebar.checkbox("INDUSTRY TRAINING I (3 kredi)")
staj2 = st.sidebar.checkbox("INDUSTRY TRAINING II (3 kredi)")

staj_courses = []
if staj1:
    staj_courses.append({"name": "INDUSTRY TRAINING I", "credit": 3, "grade": None, "type": "staj"})
if staj2:
    staj_courses.append({"name": "INDUSTRY TRAINING II", "credit": 3, "grade": None, "type": "staj"})

# Yarıyıl seçimi
semester = st.sidebar.selectbox("Yarıyıl Seç", list(predefined_courses.keys()))

# Session state hazırlığı
if "courses" not in st.session_state:
    st.session_state["courses"] = {}
if "electives" not in st.session_state:
    st.session_state["electives"] = {}

# Ders listesi göster ve not seçtir
st.subheader(f"📚 {semester} Dersleri")

entered_courses = []
for course in predefined_courses[semester]:
    grade = st.selectbox(
        f"{course['name']} ({course['credit']} kredi)", 
        list(grade_points.keys()), 
        key=f"{semester}-{course['name']}"
    )
    new_course = {
        "name": course["name"],
        "credit": course["credit"],
        "grade": grade,
        "type": "normal"
    }
    entered_courses.append(new_course)

# --- Seçmeli ders ekleme ---
with st.expander("➕ Seçmeli Ders Ekle"):
    elective_name = st.text_input("Seçmeli Ders Adı", key=f"elective-{semester}")
    elective_grade = st.selectbox("Seçmeli Ders Notu", list(grade_points.keys()), key=f"elective-grade-{semester}")
    if st.button("Ekle", key=f"add-elective-{semester}") and elective_name:
        new_elective = {"name": elective_name, "credit": 6, "grade": elective_grade, "type": "elective"}
        if semester not in st.session_state["electives"]:
            st.session_state["electives"][semester] = []
        st.session_state["electives"][semester].append(new_elective)

# --- Seçmeli dersleri anında göster + not değiştirilebilir ---
if semester in st.session_state["electives"]:
    st.write("📌 Eklenmiş Seçmeli Dersler:")
    updated_electives = []
    for i, elective in enumerate(st.session_state["electives"][semester]):
        grade = st.selectbox(
            f"{elective['name']} ({elective['credit']} kredi)",
            list(grade_points.keys()),
            index=list(grade_points.keys()).index(elective["grade"]),
            key=f"{semester}-elective-{i}"
        )
        elective["grade"] = grade
        updated_electives.append(elective)
    st.session_state["electives"][semester] = updated_electives
    entered_courses.extend(updated_electives)


# Kaydet
if st.button("💾 Kaydet"):
    all_courses = entered_courses
    st.session_state["courses"][semester] = all_courses


# Hesaplama
if st.session_state["courses"] or staj_courses:
    # Dönem bazlı
    for sem_key, courses in st.session_state["courses"].items():
        st.subheader(f"📊 {sem_key} Sonuçları")
        gpa, valid, invalid, total_gpa = calculate_gpa(courses)
        st.write(f"**GPA:** {gpa:.2f}")
        st.write(f"Stajlar Hariç TOPLAM KREDİ: {valid}")
        st.write(f"Stajlar Dahil TOPLAM KREDİ: {valid + sum(c['credit'] for c in staj_courses)}")
        if invalid > 0:
            st.write(f"Geçersiz Kredi (F Notu): {invalid}")
        st.markdown("---")

    # Genel sonuç
    all_courses = [c for sem in st.session_state["courses"].values() for c in sem]
    gpa, valid, invalid, total_gpa = calculate_gpa(all_courses)
    st.subheader("📈 Genel Sonuç")
    st.write(f"**Genel GPA:** {gpa:.2f}")
    st.write(f"Stajlar Hariç TOPLAM KREDİ: {valid}")
    st.write(f"Stajlar Dahil TOPLAM KREDİ: {valid + sum(c['credit'] for c in staj_courses)}")
    if invalid > 0:
        st.write(f"Geçersiz Kredi (F Notu): {invalid}")
