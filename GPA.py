import streamlit as st
import json
import uuid

# --- Not katsayıları ---
grade_points = {
    "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0,
    "D-": 0.7, "F": 0.0, "P": 0.0,
    "Alınmadı": None
}
grades = list(grade_points.keys())

# --- GPA hesaplama fonksiyonu ---
def calculate_gpa(courses):
    gpa_points, gpa_credits = 0.0, 0
    valid_credits, invalid_credits = 0, 0
    not_taken = []

    for course in courses:
        grade = course.get("grade")
        credit = course.get("credit", 0)

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

# --- Ön tanımlı dersler ---
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

# --- Yardımcı: yüklenen/varolan veriyi normalize et ---
def normalize_courses(courses_dict):
    out = {}
    # start by ensuring all semesters exist
    for sem in predefined_courses.keys():
        out[sem] = []

    # merge incoming
    for sem, clist in courses_dict.items():
        if sem not in out:
            out[sem] = []
        for c in clist:
            name = c.get("name")
            credit = c.get("credit", 0)
            grade = c.get("grade") or "Alınmadı"
            typ = c.get("type")
            if typ not in ("normal", "elective"):
                # determine by checking predefined
                if any(d["name"] == name for d in predefined_courses.get(sem, [])):
                    typ = "normal"
                else:
                    typ = "elective"
            cid = c.get("id") or name or str(uuid.uuid4())
            out[sem].append({"name": name, "credit": credit, "grade": grade, "type": typ, "id": cid})
    # ensure required defaults exist if missing
    for sem, defaults in predefined_courses.items():
        existing = {c["name"] for c in out[sem]}
        for d in defaults:
            if d["name"] not in existing:
                out[sem].append({"name": d["name"], "credit": d["credit"], "grade": "Alınmadı", "type": "normal", "id": d["name"]})
    return out

# --- UI Başlangıç ---
st.title("🎓 GPA Hesaplama (Stabil session_state)")

# Staj seçimi
st.sidebar.header("Stajlar")
staj1 = st.sidebar.checkbox("INDUSTRY TRAINING I (3 kredi)")
staj2 = st.sidebar.checkbox("INDUSTRY TRAINING II (3 kredi)")
staj_credits = (3 if staj1 else 0) + (3 if staj2 else 0)

# JSON yükleme
uploaded_file = st.sidebar.file_uploader("📂 Daha önce kaydedilmiş veriyi yükle", type="json")
if uploaded_file is not None:
    try:
        loaded = json.load(uploaded_file)
        st.session_state["courses"] = normalize_courses(loaded)
        st.sidebar.success("✅ Veriler yüklendi ve normalize edildi.")
    except Exception as e:
        st.sidebar.error(f"JSON okunamadı: {e}")

# İlk açılış: oluşturalım
if "courses" not in st.session_state:
    st.session_state["courses"] = normalize_courses({})

# Reset butonu (tüm notları Alınmadı yapar ve widget key'leri temizler)
if st.sidebar.button("Sıfırla (Tüm notları 'Alınmadı' yap)"):
    for sem in list(st.session_state["courses"].keys()):
        for c in st.session_state["courses"][sem]:
            c["grade"] = "Alınmadı"
    # widget key'leri temizle
    for k in list(st.session_state.keys()):
        if isinstance(k, str) and any(k.startswith(f"{sem}-") for sem in predefined_courses.keys()):
            del st.session_state[k]
    st.experimental_rerun()

# Seçmeli ekleme
st.sidebar.header("➕ Seçmeli Ders Ekle")
target_semester = st.sidebar.selectbox("Yarıyıl Seç", list(predefined_courses.keys()))
elective_name = st.sidebar.text_input("Ders Adı")
elective_credit = st.sidebar.number_input("Kredi", min_value=1, max_value=20, value=6)
elective_grade = st.sidebar.selectbox("Not", grades, key="elective-grade")

if st.sidebar.button("Ekle"):
    if elective_name.strip() == "":
        st.sidebar.warning("Ders adı boş olamaz.")
    else:
        new_id = str(uuid.uuid4())
        st.session_state["courses"].setdefault(target_semester, [])
        st.session_state["courses"][target_semester].append({
            "name": elective_name.strip(),
            "credit": elective_credit,
            "grade": elective_grade,
            "type": "elective",
            "id": new_id
        })
        st.sidebar.success(f"{target_semester} için '{elective_name}' eklendi!")
        st.experimental_rerun()

# --- Derslerin gösterimi ---
for semester in predefined_courses.keys():
    st.subheader(f"📚 {semester} Dersleri")

    # Zorunlu dersleri, predefined sırasına göre göster
    order = [d["name"] for d in predefined_courses[semester]]
    required = [c for c in st.session_state["courses"][semester] if c["type"] == "normal"]
    required_sorted = sorted(required, key=lambda x: order.index(x["name"]) if x["name"] in order else 999)

    for course in required_sorted:
        key = f"{semester}-{course['id']}"
        # widget key'i ilk defa oluşturuluyorsa default değeri koy
        if key not in st.session_state:
            st.session_state[key] = course.get("grade", "Alınmadı") or "Alınmadı"
        # selectbox (key sabit)
        st.selectbox(f"{course['name']} ({course['credit']} kredi)", grades, key=key)
        # seçilen değeri kursa yaz (in-place)
        selected = st.session_state[key]
        if course.get("grade") != selected:
            course["grade"] = selected

    # Seçmeliler
    electives = [c for c in st.session_state["courses"][semester] if c["type"] == "elective"]
    if electives:
        st.write("📌 Seçmeli Dersler:")
        for c in list(electives):  # list() kopya çünkü silme olursa sıkıntı olmasın
            key = f"{semester}-{c['id']}"
            if key not in st.session_state:
                st.session_state[key] = c.get("grade", "Alınmadı") or "Alınmadı"
            cols = st.columns([8,1])
            with cols[0]:
                st.selectbox(f"{c['name']} ({c['credit']} kredi)", grades, key=key)
            with cols[1]:
                if st.button("Sil", key=f"del-{c['id']}"):
                    st.session_state["courses"][semester] = [x for x in st.session_state["courses"][semester] if x["id"] != c["id"]]
                    # widget key temizle
                    if key in st.session_state:
                        del st.session_state[key]
                    st.experimental_rerun()
            # güncelle
            selected = st.session_state[key]
            if c.get("grade") != selected:
                c["grade"] = selected

    st.markdown("---")

# --- JSON İndir ---
st.subheader("💽 Verileri Kaydet / Yükle")
data = json.dumps(st.session_state["courses"], ensure_ascii=False, indent=2)
st.download_button("📥 JSON Olarak İndir", data=data, file_name="gpa_data.json", mime="application/json")

# --- Hesaplama ve sonuçlar ---
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
