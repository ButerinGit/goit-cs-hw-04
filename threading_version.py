# threading_version.py
from collections import defaultdict
from typing import List, Dict
from pathlib import Path
import threading
import math
import time

from common import get_text_files, read_file_text


def _thread_worker(
    files: List[Path],
    keywords: List[str],
    result: Dict[str, List[str]],
    lock: threading.Lock,
):
    """
    Функція, яка запускається в потоці.
    Проходить по своїх файлах, шукає ключові слова і записує результати в спільний словник.
    """
    keywords_lower = [k.lower() for k in keywords]

    for path in files:
        text = read_file_text(path).lower()
        if not text:
            continue

        for kw in keywords_lower:
            if kw in text:
                with lock:
                    # уникаємо дублювання шляхів
                    if path.as_posix() not in result[kw]:
                        result[kw].append(path.as_posix())


def threaded_search(
    directory: str,
    keywords: List[str],
    num_threads: int = 4,
) -> Dict[str, List[str]]:
    """
    Пошук ключових слів у всіх .txt файлах папки directory за допомогою потоків.
    Повертає словник: ключ – слово, значення – список шляхів файлів.
    """
    files = get_text_files(directory)
    if not files:
        print("Не знайдено .txt файлів у директорії.")
        return {}

    # спільний результат
    result = defaultdict(list)
    lock = threading.Lock()

    # ділимо файли на чанки для кожного потоку
    num_threads = min(num_threads, len(files))
    chunk_size = math.ceil(len(files) / num_threads)
    threads: List[threading.Thread] = []

    for i in range(num_threads):
        chunk = files[i * chunk_size : (i + 1) * chunk_size]
        if not chunk:
            continue
        t = threading.Thread(
            target=_thread_worker,
            args=(chunk, keywords, result, lock),
            daemon=True,
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # приводимо ключі до оригінального регістру ключових слів
    keywords_lower = [k.lower() for k in keywords]
    normalized_result = {kw: result[kw.lower()] for kw in keywords}
    return normalized_result


def measure_threaded(directory: str, keywords: List[str], num_threads: int = 4):
    start = time.perf_counter()
    result = threaded_search(directory, keywords, num_threads)
    end = time.perf_counter()
    print(f"[threading] Час виконання: {end - start:.4f} c")
    return result