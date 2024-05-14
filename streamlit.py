import streamlit as st

# Функция для загрузки видеофайла
def upload_video_file():
    video_file = st.file_uploader("Загрузите видеофайл партии", type=["mp4", "mov"], key="video_upload")
    if video_file is not None:
        st.success("Видеофайл успешно загружен.")   
    return video_file

# Функция для загрузки PGN-файла
def upload_pgn_file():
    pgn_file = st.file_uploader("Загрузите PGN файл партии", type="pgn", key="pgn_upload")
    if pgn_file is not None:
        st.success("PGN файл успешно загружен.")
    return pgn_file

# Функция для выгрузки видеофайла
def download_video_file(video_file):
    if video_file is not None:
        st.download_button(
            label="Скачать видеофайл",
            data=video_file,
            file_name="uploaded_video.mp4",
            mime="video/mp4"
        )

# Основная функция приложения
def main():
    st.title("Загрузка видео и PGN файлов")

    # Создание столбцов для размещения виджетов
    col1, col2 = st.columns(2)

    with col1:
        # Загрузка видеофайла
        video_file = upload_video_file()

    with col2:
        # Загрузка PGN файла
        pgn_file = upload_pgn_file()

    # Проверка, загружены ли оба файла
    if video_file is not None and pgn_file is not None:
        st.success("Оба файла успешно загружены.")
        # Добавление кнопки для выгрузки видеофайла
        download_video_file(video_file)

if __name__ == "__main__":
    main()