import asyncio

from shazamio import Shazam
import soundfile as sf
from pathlib import Path



async def musicFinder():

    shazam = Shazam()


    #Тестами було помічено, що апі аналізує не повністю аудіо файл. Зазвичай це не дуже популярні треки

    #file_path = r'D:\Platon\KPI_platon\SHAZAM_project\data\audioProces.wav'

    root_dir = Path(__file__).resolve().parent.parent.parent
    output_dir = root_dir / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / "audioProces.wav"
    print(f"Шукаємо музику за файлом: {file_path}")
    try:
        out = await shazam.recognize(str(file_path))
        print("Результат распознавания:")
        print(out)

    except Exception as eror:
        print(f"Помилка: {eror}")







if __name__ == "__main__":

    asyncio.run(musicFinder())