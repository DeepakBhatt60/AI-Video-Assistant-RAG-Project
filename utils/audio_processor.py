import yt_dlp
from pydub import AudioSegment
import subprocess
import os
import re
import uuid
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def ensure_deno():
    """Install Deno if it isn't already present, and add it to PATH.
    yt-dlp needs a JS runtime (Deno) to solve YouTube's n-parameter challenge."""
    deno_path = os.path.expanduser("~/.deno/bin/deno")
    if not os.path.exists(deno_path):
        subprocess.run(
            "curl -fsSL https://deno.land/install.sh | sh",
            shell=True,
            check=True,
        )
    os.environ["PATH"] = os.path.expanduser("~/.deno/bin") + os.pathsep + os.environ.get("PATH", "")


ensure_deno()


def extract_video_id(url: str) -> str | None:
    """Pull the 11-character YouTube video ID out of common URL formats."""
    match = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else None


def get_youtube_transcript_text(url: str) -> str | None:
    """
    Try to fetch YouTube's own captions directly — no download, no cookies,
    no Whisper/Sarvam needed. Returns None if unavailable so the caller can
    fall back to the audio-download + transcription pipeline.
    """
    video_id = extract_video_id(url)
    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join(segment["text"] for segment in transcript_list)
        text = text.strip()
        return text if text else None
    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
        return None
    except Exception:
        # Any other unexpected captions error — fall back rather than crash.
        return None


def download_youtube_audio(url: str) -> str:

    unique_id = uuid.uuid4().hex[:8]
    output_path = os.path.join(
        DOWNLOAD_DIR,
        f"{unique_id}_%(title)s.%(ext)s"
    )

    ydl_opts = {
        # Prefer a simple audio format that is widely available.
        "format": "bestaudio/best",

        "outtmpl": output_path,

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],

        "quiet": True,
        "noplaylist": True,

        # Retry transient YouTube failures.
        "retries": 3,
        "fragment_retries": 3,

        # Let yt-dlp use the installed JS runtime.
        "js_runtimes": {
            "deno": {}
        },

        # Current YouTube extractor configuration.
        "extractor_args": {
            "youtube": {
                "player_client": ["default"]
            }
        },
    }

    # Use cookies only when a real cookie file exists.
    cookie_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "cookies.txt"
    )

    if os.path.exists(cookie_file):
        ydl_opts["cookiefile"] = cookie_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            base, _ext = os.path.splitext(
                ydl.prepare_filename(info)
            )

            filename = base + ".wav"

            if not os.path.exists(filename):
                raise FileNotFoundError(
                    f"Audio conversion failed. Expected file: {filename}"
                )

            return filename

    except Exception as e:
        raise RuntimeError(
            f"Unable to download YouTube audio: {e}"
        ) from e


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # 16kHz
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start: start + chunk_ms]

        # Skip near-empty chunks (less than 0.5 sec) — these caused
        # Whisper to crash with "cannot reshape tensor of 0 elements"
        if len(chunk) < 500:
            continue

        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks
