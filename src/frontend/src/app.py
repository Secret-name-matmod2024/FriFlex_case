import streamlit as st
import tempfile
import os

# Настройка конфигурации страницы
st.set_page_config(page_title="Multi-Page App", layout="wide")


# Функция для отображения информации о задании
def display_task_info():
    st.title("Задание")
    container = st.container()
    col1, col2 = container.columns(2)

    # Добавляем CSS для стилизации текста
    st.markdown("""
    <style>
    .full-page {
        font-style: italic;
        width: 100%;
        padding: 20px;
        box-sizing: border-box;
        font-size: 1.2em; /* Увеличиваем размер шрифта */
        line-height: 1.6; /* Увеличиваем межстрочный интервал */
    }
    </style>
    """, unsafe_allow_html=True)

    with col1:
        st.image("шахмат.jpg", width=600)  # Замените на путь к вашей фотографии
    with col2:
        # Используем класс full-page для стилизации текста
        st.markdown("""
        <div class="full-page">
        В классических шахматах продолжительность партии может составлять несколько часов. Такой формат сложно воспринимается большим количеством зрителей. Короткие видеозаписи не только лучше воспринимаются для просмотра, но и помогают увеличить вовлеченность в шахматный спорт.
        </div>
        """, unsafe_allow_html=True)


def display_video_and_pgn():
    st.title("Загрузка видео и PGN-файлов")

    # Создаем две колонки
    col1, col2 = st.columns(2)

    # Виджет для загрузки видеофайла в первой колонке
    with col1:
        video_file = st.file_uploader("Загрузите видеофайл", type=["mp4", "mov", "avi", "mkv"])
        if video_file is not None:
            show_video = st.button("Показать видео")
            if show_video:
                st.video(video_file)
            download_video = st.button("Скачать видео")
            if download_video:
                # Создаем временный файл для скачивания
                temp_file_path = os.path.join(tempfile.gettempdir(), video_file.name)
                with open(temp_file_path, 'wb') as f:
                    f.write(video_file.getbuffer())
                # Предоставляем ссылку на скачивание
                with open(temp_file_path, 'rb') as f:
                    st.download_button('Скачать видео', f, file_name=video_file.name)

    # Виджет для загрузки PGN-файла во второй колонке
    with col2:
        pgn_file = st.file_uploader("Загрузите PGN-файл", type="pgn")
        if pgn_file is not None:
            st.write("Содержимое PGN-файла:")
            st.code(pgn_file.read().decode("utf-8"))


# Функция для отображения фотографий и описания
def display_photos_and_description():
    st.image("team.jpg", width=1100)  # Замените на путь к вашей фотографии


# Создание бокового меню для навигации
def create_sidebar():
    st.sidebar.title("Навигация")
    page = st.sidebar.radio("Перейти к", ("Загрузка видео и PGN-файлов", "Задание", "Наша команда"))
    return page


# Основная функция для запуска приложения
def main():
    page = create_sidebar()
    if page == "Загрузка видео и PGN-файлов":
        display_video_and_pgn()
    elif page == "Задание":
        display_task_info()
    elif page == "Наша команда":
        display_photos_and_description()


# Запуск приложения
if __name__ == "__main__":
    main()