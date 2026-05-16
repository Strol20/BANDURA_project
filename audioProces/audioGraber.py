import soundcard as sc
import soundfile as sf

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

    loopSpeaker = sc.get_microphone(speaker.id,include_loopback=True )
    print(loopSpeaker)
    return loopSpeaker




def audioRecord(microphone = None, samplerate = 41000,duration=10):
    # Тривалість в секундах
    microphone = getLoopbackMicrophone(microphone) #Перенести в audioGraber
    if (microphone == None):
        print("Не знайдено мікро, використовуємо за замовченням")
        return None
    with microphone.recorder(samplerate=samplerate,channels=2) as recorder:
        print("Початок запису на...", duration, "секунд")
        data = recorder.record(numframes=samplerate * duration)
        sf.write("filename.wav", data, samplerate)
        print("КІНЕЦЬ ЗАПИСУ")



micro = sc.all_speakers()

print(micro)

audioRecord('aaa')





