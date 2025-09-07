import streamlit as st
import json

# Harf notları
grade_points = {
    "AA": 4.0,
    "BA": 3.5,
    "BB": 3.0,
    "CB": 2.5,
    "CC": 2.0,
    "DC": 1.5,
    "DD": 1.0,
    "FF": 0.0,
    "Alınmadı": None
}

# Varsayılan dersler
default_courses = {
    "1. Yarıyıl": [
        {"name": "Matematik I", "credit": 6, "type": "normal"},
        {"name": "Fizik I", "credit": 5, "type": "normal"},
    ],
    "2. Yarıyıl": [
        {"name": "Matematik II", "credit": 6, "type": "normal"},
        {"name": "Fizik II", "credit": 5, "type": "normal"},
    ]
}

# Session state başlat
if "courses" not in st.session_state:
    st.session_state["courses"] = default_courses.copy()

# JSON yükleme
uploaded_file = st.file_uploader("📂 Daha önce kaydedilmiş veriyi yükle", type="json")
if uploaded_file is not None:
    st.session_state["courses"] = json.load(uploaded_file)
    st.success("✅ Veriler başarıyla yüklendi!")

st.title("🎓 GPA Hesaplayıcı")

# Sidebar - seçmeli ders ekleme
st.sidebar.header("➕ Seçmeli Ders Ekle")
semester_choice = st.sidebar.selectbox("Yarıyıl Seç", list(st.session_state["courses"].keys()))
new_elective = st.sidebar.text_input("Ders Adı")
new_credit = st.sidebar.number_input("Kredi", min_value=1, max_value=10, step=1)

if st.sidebar.button("Ekle"):
    if new_elective and new_credit:
        st.session_state["courses"][semester_choice].append(
            {"name": new_elective, "credit": new_credit, "type": "elective", "grade": "Alınmadı"}
        )
        st.sidebar.success(f"{semester_choice} içine {new_elective} eklendi ✅")

# Tüm yarıyıllar için dersleri göster
total_points = 0
total_credits = 0
not_taken_courses = []

for semester, courses in st.session_state["courses"].items():
    st.subheader(semester)
    to_remove = []
    for i, course in enumerate(courses):
        options = list(grade_points.keys())

        # JSON'dan gelen notu kontrol et
        if course.get("grade") in options:
            default_value = course["grade"]
        else:
            default_value = "Alınmadı"

        grade = st.selectbox(
            f"{course['name']} ({course['credit']} kredi)",
            options,
            key=f"{semester}-{course['name']}-{i}",
            value=default_value
        )

        # Güncel notu state'e yaz
        course["grade"] = grade

        if grade != "Alınmadı":
            total_points += grade_points[grade] * course["credit"]
            total_credits += course["credit"]
        else:
            not_taken_courses.append(f"{semester}: {course['name']}")

        # Sadece seçmeliler silinebilsin
        if course["type"] == "elective":
            if st.button(f"❌ {course['name']} dersini sil", key=f"remove-{semester}-{i}"):
                to_remove.append(i)

    # Silme işlemleri
    for idx in reversed(to_remove):
        del courses[idx]

# GPA hesapla
gpa = total_points / total_credits if total_credits > 0 else 0

st.markdown("---")
st.metric("📊 Genel GPA", f"{gpa:.2f}")
st.write(f"Toplam kredi (stajlar hariç): {total_credits}")

# Alınmayan dersler
if not_taken_courses:
    st.warning("📌 Bu yarıyılda alınmayan dersler:")
    for c in not_taken_courses:
        st.write(f"- {c}")

# JSON olarak indir
if st.button("📥 JSON Olarak İndir"):
    data = json.dumps(st.session_state["courses"], ensure_ascii=False, indent=2)
    st.download_button(
        label="📂 Verileri İndir",
        data=data,
        file_name="gpa_data.json",
        mime="application/json"
    )
