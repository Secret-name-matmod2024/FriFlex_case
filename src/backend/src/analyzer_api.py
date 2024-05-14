from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
from pgn_analyzer import parse_pgn, load_pgn_file, save_parsed_games, get_parsed_games, analyze_game, \
    get_interesting_moves, GameEvaluationResult, PGNAnalyzer

parser_router = APIRouter()


# Обработчик загрузки PGN файла
@parser_router.post("/upload/pgn/")
async def upload_pgn_file(pgn_file: UploadFile = File(...)):
    pgn_content = await pgn_file.read()
    parsed_games = get_parsed_games(pgn_content)
    save_parsed_games(pgn_file.filename, parsed_games)
    return {"games": parsed_games}


# Обработчик загрузки видеоролика
@parser_router.post("/upload/video/")
async def upload_video_file(video_file: UploadFile = File(...)):
    video_content = await video_file.read()
    video_filename = video_file.filename
    video_path = f"uploads/{video_filename}"
    with open(video_path, "wb") as video_writer:
        video_writer.write(video_content)
    return {"video_filename": video_filename}


# Обработчик оценки партии game_id из png_filename
@parser_router.get("/games/evaluate/{pgn_filename}/{game_id}")
async def get_interesting_moments(pgn_filename: str, game_id: int) -> GameEvaluationResult:

    try:
        analyser = PGNAnalyzer("path_to_pgn_file.pgn",
                               game_id,
                               stockfish_path='path_to_stockfish_executable.exe',
                               video_path='path_to_video_file.mp4',
                               metatool_path='path_to_exiftool_executable.exe')

        df = analyser.analyze_game(analyser.game)
        return analyser.get_interesting_moves(df)

    except KeyError:
        raise HTTPException(status_code=404, detail=f"Игра с индексом {game_id} файл не найден")
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка сервера во время анализа партии")


# # Обработчик оценки начала партии
# @parser_router.get("/estimate/{pgn_filename}/{game_id}")
# async def estimate_start(pgn_filename: str, game_id: int):
#     parsed_games = get_parsed_games(pgn_filename)
#     if not parsed_games or game_id >= len(parsed_games):
#         raise HTTPException(status_code=404, detail="Партия не найдена")
#
#     # Получаем содержимое партии из PGN файла
#     game = parsed_games[game_id]
#
#     # Эмуляция работы с видео для получения таймкода начала партии
#     video_path = f"uploads/{pgn_filename.split('.')[0]}.mp4"
#     clip = VideoFileClip(video_path)
#     # Вместо estimate_start_time можно использовать ваш алгоритм
#     estimated_time = estimate_start_time(game)
#
#     return {"pgn_filename": pgn_filename, "game_id": game_id, "estimated_start_time": estimated_time}
