from pathlib import Path
import sys

# Mendapatkan path absolut dari file saat ini
FILE = Path(__file__).resolve()
ROOT = FILE.parent

# Menambahkan path root ke sys.path jika belum ada
if ROOT not in sys.path:
    sys.path.append(str(ROOT))

# Ubah path menjadi relatif terhadap working directory saat ini
ROOT = ROOT.relative_to(Path.cwd())

# Definisi sumber
IMAGE = 'Image'
SOURCES_LIST = [IMAGE]

# Konfigurasi gambar
IMAGES_DIR = ROOT / 'images'
DEFAULT_IMAGE = IMAGES_DIR / 'hamanon_label.jpg'
DEFAULT_DETECT_IMAGE = IMAGES_DIR / 'hama_label1.jpg'
UPLOADED_IMAGES_DIR = IMAGES_DIR / 'uploaded'

# Konfigurasi model ML
MODEL_DIR = ROOT / 'weights'
DETECTION_MODEL = MODEL_DIR / 'best.pt'