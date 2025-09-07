import streamlit as st
import json

# --- Harf notlarının katsayıları ---
grade_points = {
    "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0,
    "D-": 0.7, "F": 0.0, "P": 0.0,
    "Alınmadı": None
}
GRADE_OPTIONS = list(grade_points.keys())

# --- Ön tanımlı zorunlu dersler (kopya, sabit) ---
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

SEMESTERS = list(predefined_courses.keys())

# --- Yardımcı fonksiyonlar ---
def calculate_gpa(courses):
    gpa_points = 0.0
    gpa_credits = 0
    valid_credits = 0
    invalid_credits = 0
    not_taken = []

    for course in courses:
        grade = course.get("grade", "Alınmadı")
        credit = course.get("credit", 0)
        name = course.get("name", "")

        if grade is None or grade == "Alınmadı" or grade not in grade_points:
            not_taken.append(name)
            continue

        point = grade_points.get(grade)
        if point is None:
            not_taken.append(name)
            continue

        gpa_points += point * credit
        gpa_credits += credit

        if grade == "F":
            invalid_credits += credit
        else:
            valid_credits += credit

    gpa = (gpa_points / gpa_credits) if gpa_credits > 0 else 0.0
    return gpa, valid_credits, invalid_credits, gpa_credits, not_taken

def normalize_uploaded(data):
    """Yüklenen JSON'u normalize eder:
       - Tüm yarıyılları garanti eder,
       - Her derste 'name','credit','grade','type' alanlarını tamamlar,
       - Kaybolan zorunlu dersleri ekler (Alınmadı)."""
    normalized = {}
    for sem in SEMESTERS:
        normalized[sem] = []
        uploaded_list = data.get(sem, [])

        # önce yüklenen dersleri normalize et
        for c in uploaded_list:
            nm = c.get("name", "Unnamed Course")
            cr = c.get("credit", 0)
            gr = c.get("grade", "Alınmadı")
            tp = c.get("type", "elective")
            normalized[sem].append({"name": nm, "credit": cr, "grade": gr, "type": tp})

        # eksikse zorunlu dersleri ekle (kredilerini predefined'den al)
        predefined_names = [p["name"] for p in predefined_courses.get(sem, [])]
        for p in predefined_courses.get(sem, []):
            if not any(x["name"] == p["name"] for x in normalized[sem]):
                normalized[sem].append({
                    "name": p["name"],
                    "credit": p["credit"],
                    "grade": "Alınmadı",
                    "type": "normal"
                })
    return normalized

# --- App başlangıcı ---
st.title("🎓 GPA Hesaplama Uygulaması (Geliştirilmiş)")

# Staj seçenekleri
st.sidebar.header("Stajlar")
staj1 = st.sidebar.checkbox("INDUSTRY TRAINING I (3 kredi)")
staj2 = st.sidebar.checkbox("INDUSTRY TRAINING II (3 kredi)")
staj_credits = (3 if staj1 else 0) + (3 if staj2 else 0)

# session_state "courses" yoksa default olarak normalize edilmiş ön tanımlı yapı ile doldur
if "courses" not in st.session_state:
    default_structure = {}
    for sem in SEMESTERS:
        default_structure[sem] = []
        for p in predefined_courses[sem]:
            default_structure[sem].append({
                "name": p["name"],
                "credit": p["credit"],
                "grade": "Alınmadı",
                "type": "normal"
            })
    st.session_state["courses"] = default_structure

# --- Seçmeli ders ekleme (Sidebar’dan) ---
st.sidebar.header("➕ Seçmeli Ders Ekle")
target_semester = st.sidebar.selectbox("Yarıyıl Seç", SEMESTERS)
elective_name = st.sidebar.text_input("Ders Adı")
elective_credit = st.sidebar.number_input("Kredi", min_value=1, max_value=20, value=6)
elective_grade = st.sidebar.selectbox("Not", GRADE_OPTIONS, index=GRADE_OPTIONS.index("Alınmadı"), key="elective-grade")

if st.sidebar.button("Ekle"):
    # boş isim eklemesine izin verme
    if elective_name.strip() == "":
        st.sidebar.error("Ders adı boş olamaz.")
    else:
        st.session_state["courses"][target_semester].append({
            "name": elective_name.strip(),
            "credit": elective_credit,
            "grade": elective_grade,
            "type": "elective"
        })
        st.sidebar.success(f"{target_semester} için '{elective_name}' eklendi!")

# --- JSON yükle/dışa aktar ---
st.markdown("---")
st.subheader("💽 Verileri Kaydet / Yükle")
data_to_download = json.dumps(st.session_state["courses"], ensure_ascii=False, indent=2)
st.download_button("📥 JSON Olarak İndir", data=data_to_download, file_name="gpa_data.json", mime="application/json")

uploaded_file = st.file_uploader("📂 Daha önce kaydedilmiş veriyi yükle", type="json")
if uploaded_file is not None:
    try:
        loaded = json.load(uploaded_file)
        normalized = normalize_uploaded(loaded)
        st.session_state["courses"] = normalized

        # Her ders için widget key'ini güncelle: böylece selectbox'lar doğru değeri gösterir
        for sem, course_list in st.session_state["courses"].items():
            for c in course_list:
                widget_key = f"{sem}-{c['name']}"
                st.session_state[widget_key] = c.get("grade", "Alınmadı")

        st.success("✅ Veriler başarıyla yüklendi ve arayüz güncellendi!")
        # opsiyonel: st.experimental_rerun()  # genelde gerekli değil çünkü yukarıdaki atamalar yeterli
    except Exception as e:
        st.error(f"JSON yüklemede hata: {e}")

# --- Dersleri Göster ve widget'ları senkronize et ---
for semester in SEMESTERS:
    st.subheader(f"📚 {semester} Dersleri")

    # zorunlu dersleri ve varsa seçmelileri session_state içinden alıyoruz
    sem_courses = st.session_state["courses"].get(semester, [])

    # Öncelikle zorunlu sıralamayı korumak istiyorsak, predefined listesini baz alıp render edebiliriz.
    # Burada hem zorunlu hem seçmeli hepsini gösteriyoruz:
    for course in sem_courses:
        widget_key = f"{semester}-{course['name']}"

        # widget için başlangıç değeri yoksa ata (yüklemeden gelenleri burada atıyoruz da)
        if widget_key not in st.session_state:
            st.session_state[widget_key] = course.get("grade", "Alınmadı")

        # selectbox widget (key ile bağlı)
        new_grade = st.selectbox(
            f"{course['name']} ({course['credit']} kredi) [{course.get('type','')}]",
            GRADE_OPTIONS,
            key=widget_key
        )

        # session_state içindeki derse yeni grade'i yaz (böylece hesaplama güncel kalır)
        # önce aynı isimli course varsa replace edelim, yoksa ekleyelim
        replaced = False
        for i, c in enumerate(st.session_state["courses"][semester]):
            if c["name"] == course["name"]:
                st.session_state["courses"][semester][i]["grade"] = new_grade
                replaced = True
                break
        if not replaced:
            st.session_state["courses"][semester].append({
                "name": course["name"],
                "credit": course["credit"],
                "grade": new_grade,
                "type": course.get("type", "elective")
            })

# --- Hesaplama ve Sonuçlar ---
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

    # Tüm dersleri tek listede topla
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
