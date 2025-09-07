import streamlit as st
import json
import io

# Harf notlarının katsayıları
grade_points = {
    "Alınmadı": None,
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "D+": 1.3,
    "D": 1.0,
    "F": 0.0,
}

# Ön tanımlı dönemler ve dersler
predefined_courses = {
    "Fall 2021": [
        {"name": "CALCULUS II", "credit": 7},
        {"name": "PHYSICS I", "credit": 6},
        {"name": "COMPUTER PROGRAMMING", "credit": 6},
        {"name": "TURKISH LANGUAGE I", "credit": 2},
    ],
    "Spring 2022": [
        {"name": "PHYSICS II", "credit": 6},
        {"name": "LINEAR ALGEBRA", "credit": 5},
        {"name": "ELECTRONIC CIRCUITS I", "credit": 5},
        {"name": "ELECTRONIC CIRCUITS I LABORATORY", "credit": 3},
    ],
}

st.title("🎓 GPA Hesaplama")

# Session state başlat
if "courses" not in st.session_state:
    st.session_state["courses"] = {sem: [] for sem in predefined_courses.keys()}

# JSON Yükleme
uploaded_file = st.file_uploader("📂 JSON'dan ders yükle", type="json")
if uploaded_file:
    st.session_state["courses"] = json.load(io.TextIOWrapper(uploaded_file, encoding="utf-8"))
    st.success("✅ Dersler JSON'dan yüklendi.")

# Dersleri Göster
for semester, default_courses in predefined_courses.items():
    st.subheader(f"📚 {semester} Dersleri")

    # Ön tanımlı dersler
    for course in default_courses:
        prev = next((c for c in st.session_state["courses"][semester] if c["name"] == course["name"]), None)
        current_grade = prev["grade"] if prev else "Alınmadı"

        grade = st.selectbox(
            f"{course['name']} ({course['credit']} kredi)",
            list(grade_points.keys()),
            key=f"{semester}-{course['name']}",
            index=list(grade_points.keys()).index(current_grade),
        )

        # Session_state güncelle
        if not prev or prev["grade"] != grade:
            new_course = {
                "name": course["name"],
                "credit": course["credit"],
                "grade": grade,
                "type": "normal",
            }
            st.session_state["courses"][semester] = [
                c for c in st.session_state["courses"][semester] if c["name"] != course["name"]
            ] + [new_course]

    # Eklenen seçmeli dersler
    electives = [c for c in st.session_state["courses"][semester] if c["type"] == "elective"]
    if electives:
        st.write("📌 Seçmeli Dersler:")
        new_list = []
        for i, c in enumerate(electives):
            grade = st.selectbox(
                f"{c['name']} ({c['credit']} kredi)",
                list(grade_points.keys()),
                key=f"{semester}-elective-{i}",
                index=list(grade_points.keys()).index(c["grade"]),
            )
            new_list.append(
                {"name": c["name"], "credit": c["credit"], "grade": grade, "type": "elective"}
            )
        st.session_state["courses"][semester] = [
            c for c in st.session_state["courses"][semester] if c["type"] != "elective"
        ] + new_list

    # Yeni ders ekleme
    with st.expander(f"➕ {semester} için seçmeli ders ekle"):
        new_course_name = st.text_input(f"{semester} ders adı", key=f"new-{semester}-name")
        new_course_credit = st.number_input(
            f"{semester} kredi", min_value=1, max_value=10, key=f"new-{semester}-credit"
        )
        if st.button(f"{semester} ders ekle"):
            if new_course_name:
                st.session_state["courses"][semester].append(
                    {
                        "name": new_course_name,
                        "credit": new_course_credit,
                        "grade": "Alınmadı",
                        "type": "elective",
                    }
                )
                st.success(f"✅ {semester} dönemine {new_course_name} eklendi.")

# GPA Hesaplama
total_points = 0
total_credits = 0
for semester, courses in st.session_state["courses"].items():
    for c in courses:
        if c["grade"] != "Alınmadı":
            total_points += grade_points[c["grade"]] * c["credit"]
            total_credits += c["credit"]

gpa = total_points / total_credits if total_credits > 0 else 0.0
st.subheader("📊 Sonuçlar")
st.write(f"Toplam Kredi: {total_credits}")
st.write(f"GNO: {gpa:.2f}")

# JSON Kaydetme
if st.button("💾 JSON Olarak Kaydet"):
    with open("courses.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state["courses"], f, ensure_ascii=False, indent=4)
    st.success("✅ Dersler 'courses.json' dosyasına kaydedildi.")
