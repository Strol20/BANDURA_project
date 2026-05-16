import soundcard as sc
import soundfile as sf
from pathlib import Path

def getLoopbackMicrophone(speakerName = None):
    # print(sc.all_microphones(include_loopback=True))

    # Пошук мікро яке віртуально виводить звук з навушника (loopback)
    if (speakerName == None):
        speaker = sc.default_speaker()
    else:
        try:
            speaker = sc.get_speaker(speakerName)
        except Exception as error:
            print("Error:", error)
            speaker = sc.default_speaker()

    # Пошук loopмікрофон динаміка
    loopSpeaker = sc.get_microphone(speaker.id,include_loopback=True )
    print(loopSpeaker)
    return loopSpeaker




def audioRecord(microphone = None, samplerate = 44100,duration=30):
    # Тривалість в секундах
    microphone = getLoopbackMicrophone(microphone) #Перенести в audioGraber
    if (microphone == None):
        print("Не знайдено мікро, використовуємо за замовченням")
        return None
    root_dir = Path(__file__).resolve().parent.parent
    output_dir = root_dir / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / "audioProces.wav"
    with microphone.recorder(samplerate=samplerate,channels=2) as recorder:
        print("Початок запису на...", duration, "секунд")
        data = recorder.record(numframes=samplerate * duration)
        sf.write(str(file_path), data, samplerate)
        print("КІНЕЦЬ ЗАПИСУ. Файл знаходиться в:", file_path)

def audioGraber(speakerName):
    audioRecord(getLoopbackMicrophone())


#Для тесту
#micro = sc.all_speakers()

#print(micro)

audioGraber('aaa')





