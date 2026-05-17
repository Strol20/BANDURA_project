import asyncio
import wave
import struct
import os
from shazamio import Shazam

# ──────────────────────────────────────────────
# Настройки
# ──────────────────────────────────────────────
AUDIO_FILE = "song.wav"  # путь к вашему файлу
FRAGMENT_DURATION = 10  # длина одного фрагмента в секундах
STEP = 5  # шаг между фрагментами в секундах (можно = FRAGMENT_DURATION для без перекрытия)
MAX_ATTEMPTS = 10  # сколько максимум фрагментов пробовать до первого совпадения
TMP_FRAGMENT = "_tmp_fragment.wav"


def extract_fragment(src_path: str, start_sec: float, duration_sec: float, dst_path: str) -> bool:
    """Вырезает фрагмент из WAV-файла без сторонних зависимостей."""
    with wave.open(src_path, "rb") as src:
        framerate = src.getframerate()
        n_channels = src.getnchannels()
        sampwidth = src.getsampwidth()
        n_frames = src.getnframes()

        start_frame = int(start_sec * framerate)
        duration_frames = int(duration_sec * framerate)

        if start_frame >= n_frames:
            return False  # за пределами файла

        # не выходить за конец файла
        duration_frames = min(duration_frames, n_frames - start_frame)
        if duration_frames <= 0:
            return False

        src.setpos(start_frame)
        frames = src.readframes(duration_frames)

    with wave.open(dst_path, "wb") as dst:
        dst.setnchannels(n_channels)
        dst.setsampwidth(sampwidth)
        dst.setframerate(framerate)
        dst.writeframes(frames)

    return True


def get_wav_duration(path: str) -> float:
    with wave.open(path, "rb") as f:
        return f.getnframes() / f.getframerate()


async def recognize_fragments(audio_path: str):
    shazam = Shazam()

    total_duration = get_wav_duration(audio_path)
    print(f"Файл: {audio_path}")
    print(f"Длительность: {total_duration:.1f} сек")
    print(f"Фрагмент: {FRAGMENT_DURATION} сек, шаг: {STEP} сек")
    print("─" * 50)

    attempt = 0
    start = 0.0

    while start < total_duration:
        attempt += 1
        end = min(start + FRAGMENT_DURATION, total_duration)

        print(f"[{attempt}] Фрагмент {start:.1f}–{end:.1f} сек ...", end=" ", flush=True)

        ok = extract_fragment(audio_path, start, FRAGMENT_DURATION, TMP_FRAGMENT)
        if not ok:
            print("пропуск (за пределами файла)")
            break

        try:
            result = await shazam.recognize(TMP_FRAGMENT)
        except Exception as e:
            print(f"ошибка: {e}")
            start += STEP
            continue

        matches = result.get("matches", [])
        track = result.get("track", {})

        if track:
            title = track.get("title", "?")
            subtitle = track.get("subtitle", "?")
            print(f"✅ НАЙДЕНО: {subtitle} — {title}")

            # дополнительные данные если есть
            sections = track.get("sections", [])
            for section in sections:
                if section.get("type") == "SONG":
                    meta = section.get("metadata", [])
                    for m in meta:
                        print(f"   {m.get('title')}: {m.get('text')}")
            break
        else:
            print("не распознано")

        if attempt >= MAX_ATTEMPTS:
            print(f"\nДостигнут лимит попыток ({MAX_ATTEMPTS}). Трек не найден.")
            break

        start += STEP

    else:
        print("\nФайл закончился. Трек не найден.")

    # удаляем временный файл
    if os.path.exists(TMP_FRAGMENT):
        os.remove(TMP_FRAGMENT)


if __name__ == "__main__":
    asyncio.run(recognize_fragments(AUDIO_FILE))