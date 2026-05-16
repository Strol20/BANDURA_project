import asyncio
from shazamio import Shazam


async def main():
    shazam = Shazam()

    # ИСПРАВЛЕНО: добавлен префикс r'' для сырой строки пути
    file_path = r'D:\Platon\KPI_platon\SHAZAM_project\data\audioProces.wav'

    print(f"Отправляем файл на распознавание: {file_path}")
    try:
        out = await shazam.recognize(file_path)
        print("Результат распознавания:")
        print(out)
    except Exception as e:
        print(f"Произошла ошибка при распознавании: {e}")


# Для современных версий Python вместо get_event_loop лучше использовать asyncio.run
if __name__ == "__main__":
    asyncio.run(main())