FROM ubuntu:20.04 as builder

RUN apt update && \
    apt upgrade -y && \
    apt-get install -y git make g++ wget ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    git clone https://github.com/official-stockfish/Stockfish && \
    cd Stockfish/src && \
    CXXFLAGS='-march=native' make -j2 profile-build ARCH=x86-64-bmi2


FROM python:3.9-slim

#
#RUN apt update && \
#    apt-get install -y ffmpeg && \
#    apt-get clean && \
#    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /Stockfish/src/stockfish /app/
COPY --from=builder /Stockfish/src/*.nnue /app/

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["uvicorn", "src.main:app", "--reload", "--workers", "1", "--host", "0.0.0.0", "--port", "8501"]