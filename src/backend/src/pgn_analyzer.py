import re
from datetime import datetime, timedelta

import chess
import chess.pgn
import chess.engine
import pandas as pd

import subprocess


def fill(arr):
    filled_array = []
    for i in range(len(arr) - 1):
        filled_array.append(arr[i])
        diff = arr[i + 1] - arr[i]
        if diff > 1:
            for j in range(1, diff):
                filled_array.append(arr[i] + j)
    filled_array.append(arr[-1])
    return filled_array


def split(arr):
    result = []
    i = 0
    while i < len(arr):
        subarray = [arr[i]]
        j = i + 1
        while j < len(arr) and arr[j] - arr[j - 1] <= 3:
            subarray.append(arr[j])
            j += 1
        if len(subarray) == 1:  # If only one element, fill in missing numbers
            num = subarray[0]
            for k in range(1, 4):
                if num + k in set(arr):  # Check presence using set
                    subarray.append(num + k)
        result.append(fill(subarray))  # Fill missing values inside split function
        i = j
    return result


def process_data(input_data):
    output_data = split(input_data)
    return output_data


def create_dataframe_with_ids(original_df, id_array):
    new_df = original_df[original_df['id'].isin(id_array)].copy()
    return new_df


class ChessGame:
    def __init__(self, game_id, headers):
        self.id = game_id
        default_data = {
            "Event": "?",
            "Site": "?",
            "Date": "????.??.??",
            "Round": "?",
            "White": "?",
            "Black": "?",
            "Result": "*"
        }

        self.__dict__.update(default_data)
        self.__dict__.update(headers)


from typing import List, Dict, Any


class Move:
    def __init__(self, move_number: int, video_timecode: str):
        self.move_number = move_number
        self.video_timecode = video_timecode

    def __str__(self):
        return f"Move {self.move_number}."

    def __repr__(self):
        return f"Move(move_number={self.move_number}, video_timecode='{self.video_timecode}', real_time='{self.real_time}')"


class InterestingMoment:
    def __init__(self, moves: List[Move], moment_type: str):
        self.moves = moves
        self.type = moment_type

    def __str__(self):
        moves_str = ', '.join(str(move) for move in self.moves)
        return f"InterestingMoment(type={self.type}, moves=[{moves_str}])"

    def __repr__(self):
        return f"InterestingMoment(moves={self.moves}, type='{self.type}')"


class GameEvaluationResult:
    def __init__(self, pgn_filename: str, game_id: int, interesting_moments: List[InterestingMoment]):
        self.pgn_filename = pgn_filename
        self.game_id = game_id
        self.interesting_moments = interesting_moments

    def __str__(self):
        moments_str = ', '.join(str(moment) for moment in self.interesting_moments)
        return f"GameEvaluationResult(pgn_filename='{self.pgn_filename}', game_id={self.game_id}, interesting_moments=[{moments_str}])"

    def __repr__(self):
        return f"GameEvaluationResult(pgn_filename='{self.pgn_filename}', game_id={self.game_id}, interesting_moments={self.interesting_moments})"


def parse_pgn(pgn_content):
    return pgn_content.decode().split("\n\n")


class PGNAnalyzer:
    def __init__(self, pgn_filename: str, game_id: int, stockfish_path: str, video_path: str, metatool_path: str):
        self.pgn_filename = pgn_filename
        self.game_id = game_id
        self.stockfish_path = stockfish_path
        self.video_path = video_path
        self.metatool_path = metatool_path
        self.game = self.get_parsed_game(game_id, pgn_filename)
        self.video_shift = self.get_timecode_first_move()

        time = self.get_first_move_timestamp(self.pgn_filename, self.game_id)
        self.start_move_ts = datetime.utcfromtimestamp(time / 1000)

    def get_parsed_game(self, game_id, pgn_filename):
        games = []
        with open(pgn_filename) as pgn_file:
            while True:
                game = chess.pgn.read_game(pgn_file)
                if game is None:
                    break
                games.append(game)
        return games[game_id]

    def get_parsed_games(self, pgn_content):
        games = []
        game_id = 0
        while True:
            game = chess.pgn.read_game(pgn_content)
            if game is None:
                break
            games.append(ChessGame(game_id, game.headers))
            game_id += 1
        return games

    def load_pgn_file(self, pgn_file):
        return pgn_file.read()

    def analyze_game(self, game):
        engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)

        results = []
        board = game.board()

        moves = game.mainline_moves()

        current_step = game

        for i, move in enumerate(moves):
            # Analyze the position using Stockfish
            analysis = engine.analyse(board, chess.engine.Limit(time=0.5))

            # Append the result to the list
            pattern = r"\[(\%\w+)\s(\d+)\]\[(\%\w+)\s(\d+:\d+:\d+)\]"

            # Используем re.findall для извлечения всех совпадений
            matches = re.findall(pattern, current_step.variations[0].comment)

            timestamp = ''
            timeonclock = ''

            for match in matches:
                timestamp = match[1]
                timeonclock = match[3]

            results.append({
                "id": i,
                "Move": current_step.variations[0].move,
                "Timestamp": timestamp,
                "Time on clock": timeonclock,
                "Score": analysis["score"],
                "ScoreWhite": analysis["score"].white().wdl().expectation(),
                "ScoreBlack": analysis["score"].black().wdl().expectation(),
                "ScoreRelative": analysis["score"].relative,
                "ScoreValue": analysis["score"].relative.score(mate_score=1000000),  # Convert score to centipawns,
                "Best Move": analysis["pv"][0],
            })

            board.push(move)
            current_step = current_step.variations[0]

        engine.quit()

        df = pd.DataFrame(results)
        df['df_score'] = abs(df['ScoreWhite'].diff())
        return df

    def get_interesting_moves(self, analysis_df):
        ids = process_data(
            analysis_df.sort_values(by='df_score', ascending=False)
            .head(5)
            .sort_values(by='id', ascending=True)['id']
            .tolist()
        )
        print(ids)

        moments = []
        for _ids in ids:
            df = create_dataframe_with_ids(analysis_df, _ids)
            moves = []
            for index, row in df.iterrows():
                moves.append(Move(index, video_timecode=row['Timestamp']-self.start_move_ts+self.video_shift))
            moments.append(InterestingMoment(moves, moment_type='non type'))

        return GameEvaluationResult("", 0, interesting_moments=moments)

    def get_timecode_first_move(self):
        time = self.get_first_move_timestamp(self.pgn_filename, self.game_id)
        timestamp_start = datetime.utcfromtimestamp(time / 1000)
        print(timestamp_start)

        def parse_exiftool_output(output):
            data = {}
            for line in output.split('\n'):
                match = re.match(r'^([^:]+)\s*:\s*(.*)$', line)
                if match:
                    key = match.group(1).strip()
                    value = match.group(2).strip()
                    data[key] = value
            return data

        process = subprocess.run([self.metatool_path, self.video_path], stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, input='',
                                 text=True,
                                 universal_newlines=True)

        # Получение вывода процесса
        output = process.stdout.strip()

        result_dict = parse_exiftool_output(output)
        timestamp = datetime.strptime(result_dict['Media Create Date'], "%Y:%m:%d %H:%M:%S")

        # Разбиение duration на часы, минуты и секунды
        duration_parts = list(map(int, result_dict['Media Duration'].split(":")))
        duration_delta = timedelta(hours=duration_parts[0], minutes=duration_parts[1], seconds=duration_parts[2])

        new_timestamp = timestamp - duration_delta
        return (timestamp_start - new_timestamp).total_seconds()

    def get_first_move_timestamp(self, pgn_file_path, game_id):
        games = []
        with open(pgn_file_path) as pgn_file:
            while True:
                game = chess.pgn.read_game(pgn_file)
                if game is None:
                    break
                games.append(game)

        game = games[game_id]
        pattern = r"\[(\%\w+)\s(\d+)\]\[(\%\w+)\s(\d+:\d+:\d+)\]"

        # Используем re.findall для извлечения всех совпадений
        matches = re.findall(pattern, game.variations[0].comment)

        timestamp = ''

        for match in matches:
            timestamp = match[1]

        return int(timestamp)