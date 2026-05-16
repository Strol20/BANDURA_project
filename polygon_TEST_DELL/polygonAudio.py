import soundcard as sc
import soundfile as sf


def record_directly_from_headphones(filename="shazam_input.wav", duration=7):
    try:
        # 1. Получаем устройство воспроизведения ПО УМОЛЧАНИЮ (твои наушники)
        default_speaker = sc.default_speaker()
        print(f"Успешно определен выход по умолчанию: {default_speaker.name}")

        # 2. Ищем виртуальный LOOPBACK-МИКРОФОН, привязанный к этим наушникам
        loopback_mic = sc.get_microphone(default_speaker.name, include_loopback=True)
        print(f"Для записи успешно подключен: {loopback_mic.name}")

        samplerate = 44100
        print(f"Начинаю прямой захват аудиопотока ({duration} сек)...")

        # 3. Вызываем .recorder() у МИКРОФОНА
        with loopback_mic.recorder(samplerate=samplerate) as recorder:
            # ОШИБКА ИСПРАВЛЕНА: используем правильное имя аргумента 'numframes' без подчеркивания
            data = recorder.record(numframes=samplerate * duration)

        print("Запись успешно завершена!")

        # 4. Сохраняем полученный массив данных в файл для Shazam
        sf.write(filename, data, samplerate)
        print(f"Аудио сохранено в файл: {filename}")

    except Exception as e:
        print(f"Критическая ошибка при записи через soundcard: {e}")


if __name__ == "__main__":
    # Включи музыку в наушниках HyperX и запусти код для проверки!
    record_directly_from_headphones("test_hyperx.wav", duration=5)