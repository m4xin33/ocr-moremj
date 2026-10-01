import glob
import os
import time
import cv2
from googletrans import Translator
from gtts import gTTS
import numpy as np
from PIL import Image
import pytesseract
import streamlit as st

# Configuración de página
st.set_page_config(
    page_title="Lector & Traductor Inteligente", page_icon="🔊", layout="wide"
)


# --- FUNCIONES AUXILIARES ---
def text_to_speech(input_language, output_language, text_to_convert, tld):
    translator = Translator()
    translation = translator.translate(
        text_to_convert, src=input_language, dest=output_language
    )
    trans_text = translation.text

    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)

    # Nombre de archivo seguro
    filename = f"audio_{int(time.time())}"
    filepath = f"temp/{filename}.mp3"
    tts.save(filepath)

    return filepath, trans_text


def cleanup_old_files(days=7):
    if not os.path.exists("temp"):
        os.makedirs("temp")
    mp3_files = glob.glob("temp/*.mp3")
    now = time.time()
    max_age = days * 86400
    for f in mp3_files:
        if os.stat(f).st_mtime < now - max_age:
            try:
                os.remove(f)
            except Exception:
                pass


# Limpiar archivos antiguos al iniciar
cleanup_old_files(7)

# --- DICCIONARIOS DE IDIOMAS Y ACENTOS ---
LANGUAGES = {
    "Español": "es",
    "Inglés": "en",
    "Bengalí": "bn",
    "Coreano": "ko",
    "Mandarín": "zh-cn",
    "Japonés": "ja",
}

ACCENTS = {
    "Predeterminado": "com",
    "India": "co.in",
    "Reino Unido": "co.uk",
    "Estados Unidos": "com",
    "Canadá": "ca",
    "Australia": "com.au",
    "Irlanda": "ie",
    "Sudáfrica": "co.za",
}


# --- INTERFAZ PRINCIPAL ---
st.title("🔊 Lector OCR & Traductor de Voz")
st.caption(
    "Extrae texto de una imagen (cámara o archivo), tradúcelo y escúchalo en audio."
)

# Sidebar - Configuración
with st.sidebar:
    st.header("⚙️ Configuración")

    st.subheader("1. Procesamiento de Imagen")
    aplicar_filtro = st.toggle("Invertir colores (Filtro)", value=False)

    st.subheader("2. Idioma & Audio")
    in_lang_name = st.selectbox("Idioma de origen", list(LANGUAGES.keys()), index=0)
    out_lang_name = st.selectbox(
        "Idioma a traducir", list(LANGUAGES.keys()), index=1
    )
    accent_name = st.selectbox("Acento (para Inglés)", list(ACCENTS.keys()))
    mostrar_texto_traducido = st.checkbox("Mostrar texto traducido", value=True)

    input_lang_code = LANGUAGES[in_lang_name]
    output_lang_code = LANGUAGES[out_lang_name]
    tld_code = ACCENTS[accent_name]

# Estructura principal en columnas
col_fuente, col_resultado = st.columns(2)

extracted_text = ""

with col_fuente:
    st.subheader("📸 Captura / Carga de Imagen")
    modo_origen = st.radio(
        "Selecciona el origen:",
        ["Subir Imagen", "Cámara Web"],
        horizontal=True,
    )

    cv2_img = None

    if modo_origen == "Cámara Web":
        img_buffer = st.camera_input("Toma una fotografía")
        if img_buffer is not None:
            bytes_data = img_buffer.getvalue()
            cv2_img = cv2.imdecode(
                np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR
            )
    else:
        uploaded_file = st.file_uploader(
            "Sube tu archivo", type=["png", "jpg", "jpeg"]
        )
        if uploaded_file is not None:
            file_bytes = np.asarray(
                bytearray(uploaded_file.read()), dtype=np.uint8
            )
            cv2_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            st.image(
                cv2_img,
                channels="BGR",
                caption="Imagen cargada",
                use_container_width=True,
            )

    # Procesamiento OCR si hay imagen disponible
    if cv2_img is not None:
        if aplicar_filtro:
            cv2_img = cv2.bitwise_not(cv2_img)

        img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        extracted_text = pytesseract.image_to_string(
            img_rgb, lang=input_lang_code
        ).strip()

with col_resultado:
    st.subheader("📄 Texto Detectado y Audio")

    if extracted_text:
        st.success("Texto detectado con éxito:")
        st.text_area("Texto original:", extracted_text, height=150)

        st.divider()

        if st.button("🔊 Traducir y Convertir a Voz", type="primary"):
            with st.spinner("Traduciendo y generando audio..."):
                try:
                    audio_path, translated_text = text_to_speech(
                        input_lang_code,
                        output_lang_code,
                        extracted_text,
                        tld_code,
                    )

                    st.audio(audio_path, format="audio/mp3")

                    if mostrar_texto_traducido:
                        st.markdown("### Texto Traducido:")
                        st.info(translated_text)
                except Exception as e:
                    st.error(
                        f"Error en la traducción o generación de audio: {e}"
                    )
    else:
        st.info("👈 Sube una imagen o toma una foto para comenzar.")




 
    
    
