# MV

音楽ファイルをもとに正確なLRCファイルを生成するためのCLI/WEBアプリです。Whisperで音声を文字起こしし、LRC形式に整形します。Web UIではドラッグ＆ドロップでファイルを追加し、生成されたLRCを行単位で微調整できます。

## 事前準備

- Python 3.10 以降
- `ffmpeg` がインストールされていること（`openai-whisper` の依存）。
- 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

## 使い方

```bash
python lrc_generator.py <音楽ファイルのパス> \
  --model small \            # Whisperのモデルサイズ。tiny/base/small/medium/large
  --language ja \            # 必要に応じて言語コードを指定
  --output path/to/output.lrc # 省略時は <音楽ファイル名>.lrc に出力
```

実行例:

```bash
python lrc_generator.py sample.mp3 --model small --language ja
```

## Web UI での編集 (Streamlit)

自動生成したLRCを行単位で調整したり、新規行の追加・削除を行うためのWeb UIも用意しています。音楽ファイルや歌詞ファイルはドラッグ＆ドロップで追加できます。

```bash
streamlit run app.py
```

1. サイドバーから音楽ファイル（MP3/WAV/ほか）と歌詞ファイル（TXT）をアップロード、または歌詞を直接貼り付けます。
2. 「LRCを自動生成」を押すとWhisperがタイミングを解析し、テーブルに歌詞行が並びます。
3. テーブル上で開始時刻や歌詞を直接編集できます。行の追加・削除も可能です。
4. 編集内容をLRCとしてダウンロードできます。

## 出力されるLRCの形式

```
[mm:ss.xx]歌詞テキスト
```

Whisper が返すセグメントの開始時刻ごとに、歌詞行をタイムスタンプ付きで出力します。
