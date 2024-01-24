# Python 3.11ベースイメージの使用
FROM python:3.11

# 作業ディレクトリの設定
WORKDIR /code

# 必要なパッケージのインストール
RUN apt-get update && \
    apt-get install -y less git curl && \
    rm -rf /var/lib/apt/lists/*

# llコマンドのエイリアス設定
RUN echo "alias ll='ls -l --color=auto'" >> ~/.bashrc

# FastAPIとUvicornのインストール
RUN pip install fastapi uvicorn

# アプリケーションのコピー
COPY . /code

# デフォルトコマンドの設定（Uvicornのデフォルトポート8000を使用）
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0"]