import asyncio
from audioGraber import audio_graber
from shazamioFinder import shazamio_finder



async def music_finder(speaker_name = "hyperx",duration=60,type_audio="full",iterations=1,samplerate=44100):
    generator = audio_graber(speaker_name,duration,type_audio,iterations,samplerate)
    for result in generator:
        music_analis = await shazamio_finder(result)
        if not music_analis:
            music_analis = {}
        matches = music_analis.get("matches", [])
        track = music_analis.get("track", {})
        if track:
            title = track.get("title", "?")
            subtitle = track.get("subtitle", "?")
            print(f"✅ НАЙДЕНО: {subtitle} — {title}")
            return {title,subtitle}
        else:
            print("❌ Трек не знайдено.")


        print("result")

speaker_name = "Hyperx"
duration=3
type_audio="chunk"
iterations=5
samplerate=44100

asyncio.run(music_finder(speaker_name,duration,type_audio,iterations,samplerate))