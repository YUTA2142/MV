"""
Streamlit app for generating and editing LRC files with Whisper.
"""
from __future__ import annotations

import pathlib
import tempfile
from typing import Iterable, List

import pandas as pd
import streamlit as st
import whisper

from lrc_generator import format_timestamp


@st.cache_resource(show_spinner=False)
def load_model(model_size: str):
    """Cache Whisper model to avoid reloading between requests."""
    return whisper.load_model(model_size)


def parse_timestamp(value: str) -> float:
    """Parse mm:ss.xx strings into seconds."""
    cleaned = value.strip().strip("[]")
    if not cleaned:
        return 0.0
    try:
        minutes, rest = cleaned.split(":", 1)
        return int(minutes) * 60 + float(rest)
    except ValueError:
        return 0.0


def rows_to_lrc(rows: Iterable[dict]) -> str:
    """Convert editable rows back into LRC content."""
    lines = []
    for row in rows:
        timestamp = str(row.get("timestamp", "")).strip()
        lyric = str(row.get("lyric", "")).strip()
        if not timestamp or not lyric:
            continue
        seconds = parse_timestamp(timestamp)
        lines.append((seconds, f"[{format_timestamp(seconds)}]{lyric}"))
    lines.sort(key=lambda pair: pair[0])
    return "\n".join(line for _, line in lines)


def align_segments_with_lyrics(segments: List[dict], lyrics_text: str) -> list[dict]:
    """Return editable rows using provided lyrics or Whisper text."""
    provided_lines = [line.strip() for line in lyrics_text.splitlines() if line.strip()]
    rows: list[dict] = []
    if provided_lines:
        for index, text in enumerate(provided_lines):
            if segments:
                start = segments[min(index, len(segments) - 1)].get("start", 0.0)
            else:
                start = float(index * 3)
            rows.append({"timestamp": format_timestamp(start), "lyric": text})
    else:
        for segment in segments:
            text = segment.get("text", "").strip()
            if not text:
                continue
            rows.append({
                "timestamp": format_timestamp(segment.get("start", 0.0)),
                "lyric": text,
            })
    return rows


def read_lyrics(uploaded_file, manual_text: str) -> str:
    if manual_text.strip():
        return manual_text
    if uploaded_file:
        content = uploaded_file.read()
        try:
            return content.decode("utf-8")
        except Exception:
            return content.decode("utf-8", errors="ignore")
    return ""


def transcribe_audio(audio_file, model_size: str, language: str | None) -> List[dict]:
    suffix = pathlib.Path(audio_file.name).suffix or ".tmp"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(audio_file.read())
        temp_path = pathlib.Path(temp.name)
    model = load_model(model_size)
    result = model.transcribe(str(temp_path), language=language, word_timestamps=False)
    temp_path.unlink(missing_ok=True)
    return result.get("segments", [])


def main() -> None:
    st.title("LRCエディター")
    st.write("音声から自動生成したLRCを手動で微調整できます。音源と歌詞テキストをアップロードして開始してください。")

    with st.sidebar:
        st.header("ファイルアップロード")
        audio_file = st.file_uploader(
            "音楽ファイル", type=["mp3", "wav", "m4a", "flac", "ogg"], accept_multiple_files=False
        )
        lyric_file = st.file_uploader("歌詞ファイル (TXT)", type=["txt"], accept_multiple_files=False)
        manual_lyrics = st.text_area("歌詞テキスト (任意)", placeholder="ここに歌詞を貼り付けてもOKです")

        st.header("オプション")
        model_size = st.selectbox(
            "Whisperモデルサイズ",
            options=["tiny", "base", "small", "medium", "large"],
            index=2,
        )
        language = st.text_input("言語コード (例: ja, en)", value="") or None

    st.divider()
    if "rows" not in st.session_state:
        st.session_state.rows = []

    generate_clicked = st.button("LRCを自動生成", type="primary", disabled=audio_file is None)
    if generate_clicked:
        if not audio_file:
            st.error("先に音楽ファイルをアップロードしてください。ドラッグ＆ドロップも利用できます。")
        else:
            with st.spinner("Whisperでタイミングを解析中..."):
                segments = transcribe_audio(audio_file, model_size, language)
            lyrics_text = read_lyrics(lyric_file, manual_lyrics)
            st.session_state.rows = align_segments_with_lyrics(segments, lyrics_text)
            st.success("LRCを生成しました。下の表で自由に編集できます。行の追加・削除も可能です。")

    st.subheader("歌詞行の編集")
    st.write("タイムスタンプや歌詞を直接編集し、新しい行の追加や不要な行の削除も行えます。")

    edited = st.data_editor(
        pd.DataFrame(st.session_state.rows),
        num_rows="dynamic",
        column_config={
            "timestamp": st.column_config.TextColumn(
                "開始時刻 (mm:ss.xx)", help="例: 00:12.50 のように入力してください"
            ),
            "lyric": st.column_config.TextColumn("歌詞"),
        },
        key="editable_table",
    )

    lrc_content = rows_to_lrc(edited.to_dict(orient="records")) if not edited.empty else ""

    st.download_button(
        "編集済みLRCをダウンロード",
        data=lrc_content,
        file_name="edited.lyrics.lrc",
        mime="text/plain",
        disabled=not lrc_content,
    )

    st.caption("音楽ファイルや歌詞ファイルはドラッグ＆ドロップで追加できます。生成後は表で微調整し、LRCとして保存してください。")


if __name__ == "__main__":
    main()
