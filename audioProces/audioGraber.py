import soundcard as sc
import soundfile as sf
from pathlib import Path


def get_loopback_microphone(speaker_name=None):
    # print(sc.all_microphones(include_loopback=True))

    # Пошук мікро яке віртуально виводить звук з навушника (loopback)
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




def audioRecord(microphone=None, duration=30, samplerate=44100):
    # Тривалість в секундах
    microphone = get_loopback_microphone(microphone)  #Перенести в audioGraber
    if microphone is None:
        print("Не знайдено мікро, використовуємо за замовченням")
        return None
    root_dir = Path(__file__).resolve().parent.parent
    output_dir = root_dir / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / "audioProces.wav"
    with microphone.recorder(samplerate=samplerate, channels=2) as recorder:
        print("Початок запису на...", duration, "секунд")
        data = recorder.record(numframes=samplerate * duration)
        print(data)
        sf.write(str(file_path), data, samplerate)
        print("КІНЕЦЬ ЗАПИСУ. Файл знаходиться в:", file_path)

def audioGraber(speakerName):
    audioRecord(get_loopback_microphone())


#Для тесту
#micro = sc.all_speakers()

#print(micro)

audioGraber('aaa')





