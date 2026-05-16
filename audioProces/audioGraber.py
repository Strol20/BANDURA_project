import soundcard as sc
import soundfile as sf

def audio_Graber(speakerName = None, samplerate = 44100):
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
    loopSpeaker = sc.get_microphone(speaker.name,include_loopback=True )
    print(loopSpeaker)


micro = sc.all_speakers()

print(micro)

audio_Graber('aaa')



