from pathlib import Path
import PIL
from datetime import datetime
import pytz
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Float, Table, MetaData, DateTime, LargeBinary
from sqlalchemy.orm import sessionmaker
import settings
import helper
import io

# --- CONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Deteksi Hama pada Melon",
    page_icon="🍈",
    layout="wide",
)

# --- CSS TAMBAHAN UNTUK UI/UX ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }
        .stButton > button {
            width: 100%;
        }
        .stSidebar {
            background-color: #f8f9fa;
        }
        .result-box {
            border: 1px solid #eee;
            border-radius: 10px;
            padding: 15px;
            background-color: #fafafa;
        }
    </style>
""", unsafe_allow_html=True)

# --- SETUP DATABASE ---
engine = create_engine('sqlite:///detection_results.db')
metadata = MetaData()

detections_table = Table(
    'detections', metadata,
    Column('id', Integer, primary_key=True),
    Column('image_name', String),
    Column('detection_confidence', Float),
    Column('detection_data', String),
    Column('detection_time', DateTime, default=datetime.utcnow),
    Column('image_data', LargeBinary)
)

metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# --- NAVIGASI UTAMA ---
if 'page' not in st.session_state:
    st.session_state.page = "Home"

st.sidebar.title("📍 Menu")
st.session_state.page = st.sidebar.radio(
    "Navigasi",
    options=["Home", "Deteksi", "Riwayat Deteksi"],
)

# --- HALAMAN HOME (Galeri & Edukasi Hama) ---
if st.session_state.page == "Home":
    st.title("🏠 Aplikasi Deteksi Hama pada Melon")
    st.markdown("Selamat datang di aplikasi deteksi hama pada tanaman melon. Aplikasi ini dirancang untuk membantu petani dan praktisi pertanian dalam mengidentifikasi hama-hama yang umum menyerang tanaman melon, serta memberikan informasi tentang cara pengendaliannya.")

    st.subheader("🔍 Contoh Hasil Deteksi")
    st.markdown("Berikut adalah perbandingan antara gambar sebelum dan sesudah proses deteksi dilakukan oleh sistem.")
    col1, col2 = st.columns(2)
    with col1:
        st.image("images/hamanon_label.jpg", caption="Gambar Default", use_column_width=True)
    with col2:
        st.image("images/hama_label1.jpg", caption="Gambar Setelah Deteksi", use_column_width=True)

    st.markdown("---")

    st.subheader("📚 Informasi Jenis-Jenis Hama Pada Melon")

    # Aphids
    st.markdown("### 🐜 Aphids (Kutu Daun)")
    st.image("images/aphids.jpg", caption="Contoh Aphids (Kutu Daun)", width=300)
    st.markdown("""
**Deskripsi:** Aphids (Kutu Daun) adalah serangga kecil yang menyerang tanaman melon dengan mengisap cairan dari bagian tanaman muda seperti daun dan pucuk. Akibat serangan aphids, daun dapat menjadi keriting, pertumbuhan tanaman terhambat, dan kualitas buah menurun. Aphids juga berperan sebagai vektor virus yang menyebabkan penyakit pada melon.

**Cara Mengatasi:**
- Pengendalian Biologis: Memanfaatkan musuh alami seperti larva syrphid dan kumbang ladybird.
- Pengendalian Budaya: Penggunaan mulsa reflektif dan penghindaran pemupukan nitrogen berlebihan.
- Pengendalian Kimia: Gunakan insektisida sistemik secara selektif dan sesuai anjuran.

*Sumber: [ephytia.inrae.fr - Melon Aphids](https://ephytia.inrae.fr/en/C/7979/Melon-Aphids)*
""")

    st.markdown("---")

    # Red Pumpkin Beetle
    st.markdown("### 🐞 Red Pumpkin Beetle (Kumbang Merah)")
    st.image("images/redmelonbeetle.jpg", caption="Contoh Red Pumpkin Beetle (Kumbang Merah)", width=300)
    st.markdown("""
**Deskripsi:** Red Pumpkin Beetle (Aulacophora foveicollis) atau Kumbang Merah Melon adalah hama penting pada tanaman melon yang menyerang daun, batang, dan buah. Kumbang dewasa memakan bagian daun, sedangkan larva menyerang akar. Serangan parah dapat menyebabkan tanaman menjadi layu bahkan mati, terutama pada fase awal pertumbuhan.

**Cara Mengatasi:**
- Pengendalian Budaya: Rotasi tanaman, penggunaan mulsa plastik, dan penyiangan rutin.
- Pengendalian Kimia: Gunakan insektisida seperti karbamat dan piretroid secara bijak.

*Sumber: [katyayanikrishidirect.com](https://katyayanikrishidirect.com/blogs/news/best-ways-to-control-red-pumpkin-beetle-in-watermelon)*
""")

    st.markdown("---")

    # Melonworm
    st.markdown("### 🐛 Melonworm atau Ulat Daun")
    st.image("images/melonworm.jpg", caption="Contoh Melonworm atau Ulat Daun ", width=300)
    st.markdown("""
**Deskripsi:** Melonworm atau Ulat Daun merupakan jenis ulat dari golongan noctuids yang menyerang daun tanaman melon. Serangan parah dapat menyebabkan daun habis dimakan (defoliasi), mengganggu fotosintesis, dan menurunkan hasil panen.

**Cara Mengatasi:**
- Pengendalian Budaya: Gunakan perangkap feromon dan jaring pelindung.
- Pengendalian Biologis: Aplikasi *Bacillus thuringiensis* (Bt) untuk ulat muda sangat efektif.
- Pengendalian Kimia: Penggunaan insektisida selektif jika populasi tinggi.

*Sumber: [ephytia.inrae.fr - Melonworm ](https://ephytia.inrae.fr/en/C/8027/Melon-Moths-noctuids)*
""")

    st.markdown("---")

    # Whitefly
    st.markdown("### 🪰 Whitefly (Lalat Putih)")
    st.image("images/Whitefly.webp", caption="Contoh Whitefly (Lalat Putih)", width=300)
    st.markdown("""
**Deskripsi:** Whiteflies (Lalat Putih) adalah hama kecil berwarna putih yang menyerang bagian bawah daun melon. Mereka mengisap getah tanaman dan mengeluarkan embun madu yang menyebabkan tumbuhnya jamur jelaga. Akibatnya, fotosintesis terganggu dan tanaman menjadi lemah.

**Cara Mengatasi:**
- Pengendalian Budaya: Menjaga sanitasi kebun dan mengatur jarak tanam.
- Pengendalian Biologis: Memanfaatkan musuh alami seperti Encarsia formosa (tawon parasit) dan kumbang predator.
- Pengendalian Kimia: Aplikasi insektisida selektif bila populasi tidak terkendali.

*Sumber: [ephytia.inrae.fr - Melon Whiteflies](https://ephytia.inrae.fr/en/C/7978/Melon-Whiteflies)*
""")

    st.markdown("---")

    # Stink Bug
    st.markdown("### 🪳 Stink Bug (Kepik Penghisap Buah)")
    st.image("images/stinkbug.jpg", caption="Contoh Stink Bug (Kepik Penghisap Buah)", width=300)
    st.markdown("""
**Deskripsi:** Stink Bug (Kepik Penghisap Buah) adalah hama yang termasuk dalam keluarga *Pentatomidae*. Mereka menyerang buah melon dengan cara menusuk dan mengisap cairan dari dalam buah. Akibat serangan ini, buah akan mengalami kerusakan berupa bercak nekrotik (berwarna coklat) di permukaan dan bagian dalam buah. Kerusakan ini tidak hanya mengurangi nilai jual tetapi juga kualitas konsumsi buah.

**Cara Mengatasi:**
- **Pengendalian Budaya:** Penyiangan gulma secara rutin untuk mengurangi tempat berlindung stink bug.
- **Pengendalian Biologis:** Memanfaatkan musuh alami seperti *Trissolcus basalis* (tawon parasit telur).
- **Pengendalian Kimia:** Aplikasi insektisida kontak seperti piretroid secara hati-hati, dengan memperhatikan fase tanaman dan populasi hama.

*Sumber: [edis.ifas.ufl.edu - Stink Bugs in Vegetable Crops](https://edis.ifas.ufl.edu/publication/IN623)*
""")

    st.markdown("---")

    #Thrips
    st.markdown("### 🌿 Thrips ")
    st.image("images/thrips.webp", caption="Contoh Thrips", width=300)
    st.markdown("""
*Deskripsi:* Thrips adalah serangga kecil ramping yang biasanya menyerang bagian bawah daun, bunga, dan buah melon. Mereka menyebabkan kerusakan dengan mengisap cairan tanaman dan meninggalkan bercak keperakan atau cokelat pada permukaan daun. Serangan berat dapat menyebabkan pertumbuhan tanaman terhambat, daun menjadi menggulung, serta menurunkan kualitas dan kuantitas buah.

*Cara Mengatasi:*
- *Pengendalian Budaya:* Menjaga kebersihan lahan dan membuang bagian tanaman yang terinfeksi.
- *Pengendalian Biologis:* Melepas musuh alami seperti Orius spp. (kumbang predator).
- *Pengendalian Kimia:* Gunakan insektisida selektif berbahan aktif seperti spinosad dengan rotasi bahan aktif untuk mencegah resistensi.

Sumber: [ephytia.inrae.fr - Melon Thrips](https://ephytia.inrae.fr/en/C/7980/Melon-Thrips)
""")

    st.markdown("---")

    #Fruitfly
    st.markdown("### 🪰 Melon Fruit Fly (Lalat Buah Melon)")
    st.image("images/melonfruitfly.jpg", caption="Contoh Melon Fruit Fly (Lalat Buah Melon)", width=300)
    st.markdown("""
*Deskripsi:* Melon Fruit Fly (Bactrocera cucurbitae) atau Lalat Buah Melon merupakan hama utama pada tanaman melon dan famili cucurbit lainnya. Betina dewasa meletakkan telur di bawah kulit buah muda. Setelah menetas, larva (belatung) menggali ke dalam daging buah dan menyebabkan kerusakan berupa pembusukan. Serangan berat dapat menyebabkan kerugian panen yang signifikan dan mengurangi nilai jual buah.

*Cara Mengatasi:*
- *Pengendalian Budaya:* Pemetikan dan pemusnahan buah yang terinfeksi, sanitasi area kebun, dan rotasi tanaman.
- *Pengendalian Mekanis:* Penggunaan perangkap atraktan berbasis metil eugenol untuk menangkap lalat jantan.
- *Pengendalian Kimia:* Aplikasi insektisida umpan (bait spray) secara selektif pada area sekitar tanaman.

Sumber: [Alameda County - Melon Fruit Fly](https://www.acgov.org/cda/awm/agprograms/pestdetection/melonfruitfly.htm)
""")

    st.markdown("---")
    st.info("Untuk melakukan deteksi secara langsung, silakan pergi ke halaman **Deteksi** pada menu di samping.")

# --- HALAMAN DETEKSI ---
elif st.session_state.page == "Deteksi":
    st.title("🐛 Deteksi Hama pada Melon")
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    uploaded_file = None
    uploaded_image = None
    result_img = None

    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.subheader("⚙️ Konfigurasi Model")
        confidence = float(st.slider("Tingkat Keyakinan (%)", 0, 100, 10)) / 100
        model_path = Path(settings.DETECTION_MODEL)

        try:
            model = helper.load_model(model_path)
            st.success("Model berhasil dimuat.")
        except Exception as ex:
            st.error(f"Gagal memuat model dari: {model_path}")
            st.error(ex)

        st.subheader("📁 Upload Gambar")
        uploaded_file = st.file_uploader("Pilih gambar (jpg/png/webp)...", type=["jpg", "jpeg", "png", "webp"])
        if uploaded_file:
            uploaded_image = PIL.Image.open(uploaded_file)

        if uploaded_file and st.button("🔍 Jalankan Deteksi"):
            try:
                result = model.predict(uploaded_image, conf=confidence)
                result_img = result[0].plot()[:, :, ::-1]

                buf = io.BytesIO()
                PIL.Image.fromarray(result_img).save(buf, format="PNG")
                image_bytes = buf.getvalue()

                detection_data = [str(box.data) for box in result[0].boxes]
                session.execute(detections_table.insert().values(
                    image_name=f"processed_{uploaded_file.name}",
                    detection_confidence=confidence,
                    detection_data=",".join(detection_data),
                    detection_time=datetime.utcnow(),
                    image_data=image_bytes
                ))
                session.commit()
                st.success("✅ Hasil deteksi berhasil disimpan.")
                st.session_state.result_img = result_img
            except Exception as ex:
                st.error("❌ Terjadi kesalahan saat deteksi.")
                st.error(ex)
        elif not uploaded_file:
            st.session_state.result_img = None
        else:
            st.session_state.result_img = None

    with col2:
        st.subheader("📌 Tata Cara Deteksi")
        st.markdown("""
        1. **Unggah gambar** hama dalam format `.jpg`, `.jpeg`, `.png`, atau `.webp`.
        2. **Atur tingkat keyakinan (confidence)** sesuai kebutuhan.
        3. Klik tombol **🔍 Jalankan Deteksi** untuk memulai proses pendeteksian hama.
        4. Hasil deteksi akan ditampilkan di bawah.
        5. Hasil akan tersimpan secara otomatis dan dapat dilihat kembali di menu **Riwayat Deteksi**.
        """)

    st.markdown("---")
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🖼️ Pratinjau Gambar")
        if uploaded_file:
            st.image(uploaded_file, caption="Gambar yang Diunggah", use_column_width=True)
        else:
            st.info("Silakan unggah gambar terlebih dahulu.")

    with col_right:
        st.subheader("🎯 Hasil Deteksi")
        if uploaded_file and st.session_state.result_img is None:
            st.info("Klik tombol '🔍 Jalankan Deteksi' untuk melihat hasil.")
        elif st.session_state.result_img is not None:
            st.image(st.session_state.result_img, caption="Hasil Deteksi", use_column_width=True)

# --- HALAMAN RIWAYAT DETEKSI ---
elif st.session_state.page == "Riwayat Deteksi":
    st.title("📂 Riwayat Deteksi")
    try:
        results = session.query(detections_table).order_by(detections_table.c.detection_time.desc()).all()
        if not results:
            st.info("Belum ada hasil deteksi yang disimpan.")
        else:
            local_tz = pytz.timezone("Asia/Jakarta")
            for row in results:
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown("### 📝 Info Deteksi")
                        st.markdown(f"**Nama Gambar:** {row.image_name}")
                        st.markdown(f"**Confidence:** {row.detection_confidence * 100:.1f}%")
                        time_local = row.detection_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
                        st.markdown(f"**Waktu:** {time_local.strftime('%Y-%m-%d %H:%M:%S')}")
                        if row.image_data:
                            img = PIL.Image.open(io.BytesIO(row.image_data))
                            st.image(img, caption="Gambar Hasil Deteksi", use_column_width=True)
                        else:
                            st.warning("Tidak ada gambar.")
                    with col2:
                        if st.button("🗑️ Hapus", key=f"hapus_{row.id}"):
                            session.query(detections_table).filter_by(id=row.id).delete()
                            session.commit()
                            st.success("Hasil deteksi dihapus.")
                            st.experimental_rerun()
                    st.markdown("---")
    except Exception as e:
        st.error("Gagal mengambil data dari database.")
        st.error(e)
