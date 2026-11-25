# 설치 방법:
#   macOS:   brew install ffmpeg
#   Ubuntu:  sudo apt install ffmpeg
#   Windows: winget install Gyan.FFmpeg
# ffprobe가 PATH에 등록되어 있어야 합니다.

import json
import shutil
import subprocess
from pathlib import Path


def format_size(size_bytes: int) -> str:
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size_bytes} B"


def main() -> None:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        print("오류: ffprobe를 찾을 수 없습니다. FFmpeg를 설치하고 PATH를 확인하세요.")
        return

    raw_path = input("동영상 파일 경로를 입력하세요: ").strip().strip('"')
    video_path = Path(raw_path).expanduser()

    if not video_path.is_file():
        print(f"오류: 파일을 찾을 수 없습니다: {video_path}")
        return

    command = [
        ffprobe,
        "-v", "error",
        "-show_entries",
        "format=duration,format_name:stream=codec_type,codec_name,width,height",
        "-of", "json",
        str(video_path),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        metadata = json.loads(result.stdout)
        file_size = video_path.stat().st_size
    except subprocess.CalledProcessError as exc:
        print("오류: ffprobe가 파일 정보를 읽지 못했습니다.")
        if exc.stderr:
            print(exc.stderr.strip())
        return
    except (json.JSONDecodeError, OSError) as exc:
        print(f"오류: 메타 정보를 처리하지 못했습니다: {exc}")
        return

    format_info = metadata.get("format", {})
    streams = metadata.get("streams", [])
    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]

    try:
        duration = float(format_info["duration"])
        duration_text = f"{duration:.2f}초 ({duration / 60:.2f}분)"
    except (KeyError, TypeError, ValueError):
        duration_text = "알 수 없음"

    print("\n동영상 메타 정보")
    print(f"파일 경로: {video_path.resolve()}")
    print(f"파일 크기: {file_size:,} bytes ({format_size(file_size)})")
    print(f"길이: {duration_text}")
    print(f"컨테이너 형식: {format_info.get('format_name', '알 수 없음')}")

    if video_streams:
        for index, stream in enumerate(video_streams, start=1):
            resolution = (
                f"{stream['width']}x{stream['height']}"
                if "width" in stream and "height" in stream
                else "알 수 없음"
            )
            print(f"비디오 스트림 {index} 해상도: {resolution}")
            print(f"비디오 스트림 {index} 코덱: {stream.get('codec_name', '알 수 없음')}")
    else:
        print("비디오 스트림: 없음")

    if audio_streams:
        for index, stream in enumerate(audio_streams, start=1):
            print(f"오디오 스트림 {index} 코덱: {stream.get('codec_name', '알 수 없음')}")
    else:
        print("오디오 스트림: 없음")


if __name__ == "__main__":
    main()