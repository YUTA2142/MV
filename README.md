# MV

音楽ファイルをもとに正確なLRCファイルを生成するためのCLIアプリです。Whisperで音声を文字起こしし、LRC形式に整形します。

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

## 出力されるLRCの形式

```
[mm:ss.xx]歌詞テキスト
```

Whisper が返すセグメントの開始時刻ごとに、歌詞行をタイムスタンプ付きで出力します。
