"""
CLI tool to create LRC files from music/audio files using Whisper transcription.
"""
from __future__ import annotations

import argparse
import pathlib
from typing import Iterable

import whisper


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an LRC file by transcribing an audio file with Whisper."
    )
    parser.add_argument("audio", type=pathlib.Path, help="Path to the input audio file")
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        help="Destination path for the generated LRC file (defaults to <audio>.lrc)",
    )
    parser.add_argument(
        "-m",
        "--model",
        default="small",
        help="Whisper model size to use (tiny, base, small, medium, large)",
    )
    parser.add_argument(
        "-l",
        "--language",
        dest="language",
        help="Language code to hint to Whisper (e.g. ja, en).",
    )
    return parser.parse_args()


def format_timestamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:05.2f}"


def segments_to_lrc(segments: Iterable[dict]) -> str:
    lines = []
    for segment in segments:
        start = format_timestamp(segment["start"])
        text = segment.get("text", "").strip()
        if not text:
            continue
        lines.append(f"[{start}]{text}")
    return "\n".join(lines)


def transcribe(audio_path: pathlib.Path, model_size: str, language: str | None) -> str:
    model = whisper.load_model(model_size)
    result = model.transcribe(str(audio_path), language=language, word_timestamps=False)
    return segments_to_lrc(result.get("segments", []))


def main() -> None:
    args = parse_args()
    audio_path: pathlib.Path = args.audio
    if not audio_path.exists():
        raise SystemExit(f"Audio file not found: {audio_path}")

    output_path = args.output or audio_path.with_suffix(".lrc")

    lrc_content = transcribe(audio_path, args.model, args.language)
    output_path.write_text(lrc_content, encoding="utf-8")
    print(f"Generated LRC: {output_path}")


if __name__ == "__main__":
    main()
