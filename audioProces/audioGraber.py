import io
import soundcard as sc
import soundfile as sf
from pathlib import Path


def get_loopback_microphone(speaker_name=None):
    # print(sc.all_microphones(include_loopback=True))

    # Пошук мікро яке віртуально виводить звук з навушника (loopback)
    #Пошук за назвою або обирає дефолтний
    if speaker_name is None:
        speaker = sc.default_speaker()
    else:
        try:
            speaker = sc.get_speaker(speaker_name)
        except Exception as error:
            print("Error:", error)
            speaker = sc.default_speaker()

    # Пошук loopмікрофон динаміка
    loopSpeaker = sc.get_microphone(speaker.id, include_loopback=True )
    print(loopSpeaker)
    return loopSpeaker




def audioRecord(microphone=None, duration=60, type_audio="full", iterations=1, samplerate=44100):
    # Тривалість в секундах
    if microphone is None:
        print("Не знайдено мікро, використовуємо за замовченням")
        return None
    #Шлях до тимчасового файлу
    root_dir = Path(__file__).resolve().parent.parent
    output_dir = root_dir / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / "audioProces.wav"


    #Запис аудіо
    with microphone.recorder(samplerate=samplerate, channels=2) as recorder:
        if type_audio == "chunk":
            for i in range(iterations):
                print("Початок запису на...", duration, "секунд. Залишилося", range(iterations), "ітерацій")
                # samplerate * duration = дліна запису
                data = recorder.record(numframes=samplerate * duration)
                print("data")

                wav_io = io.BytesIO()
                sf.write(wav_io, data, samplerate, format='WAV', subtype='PCM_16')
                wav_bytes = wav_io.getvalue()
                wav_io.close()
                print("КІНЕЦЬ ЗАПИСУ.Повернення кеш файлу")
                yield wav_bytes
        elif type_audio == "full":
            print("Початок запису на...", duration, "секунд")
            # samplerate * duration = дліна запису
            data = recorder.record(numframes=samplerate * duration)
            sf.write(str(file_path), data, samplerate)
            print("КІНЕЦЬ ЗАПИСУ. Файл знаходиться в:", file_path)
            yield str(file_path)
        else:
            print("Непрвальний тип запису")


def audio_graber(speakerName, duration=60, type_audio="full", iterations=1, samplerate=44100):
    return audioRecord(get_loopback_microphone(speakerName), duration, type_audio, iterations, samplerate)




#Для тесту
#micro = sc.all_speakers()

#print(micro)

#audio_graber('aaa')





