# multiprocessing_version.py
from collections import defaultdict
from typing import List, Dict
from pathlib import Path
import math
import time
from multiprocessing import Process, Queue, cpu_count

from common import get_text_files, read_file_text


def _process_worker(
    files: List[Path],
    keywords: List[str],
    queue: Queue,
):
    """
    Функція, яка запускається в окремому процесі.
    Повертає результати через Queue.
    """
    local_result = defaultdict(list)
    keywords_lower = [k.lower() for k in keywords]

    for path in files:
        text = read_file_text(path).lower()
        if not text:
            continue

        for kw in keywords_lower:
            if kw in text:
                if path.as_posix() not in local_result[kw]:
                    local_result[kw].append(path.as_posix())

    # відправляємо результат головному процесу
    queue.put(dict(local_result))


def multiprocessing_search(
    directory: str,
    keywords: List[str],
    num_processes=None,
) -> Dict[str, List[str]]:
    files = get_text_files(directory)
    if not files:
        print("Не знайдено .txt файлів у директорії.")
        return {}

    if num_processes is None:
        num_processes = cpu_count()

    num_processes = min(num_processes, len(files))
    chunk_size = math.ceil(len(files) / num_processes)

    queue: Queue = Queue()
    processes: List[Process] = []

    for i in range(num_processes):
        chunk = files[i * chunk_size : (i + 1) * chunk_size]
        if not chunk:
            continue
        p = Process(target=_process_worker, args=(chunk, keywords, queue))
        processes.append(p)
        p.start()

    # збираємо часткові результати
    final_result = defaultdict(list)

    for _ in processes:
        part = queue.get()  # словник від одного процесу
        for kw, paths in part.items():
            for pth in paths:
                if pth not in final_result[kw]:
                    final_result[kw].append(pth)

    for p in processes:
        p.join()

    normalized_result = {kw: final_result[kw.lower()] for kw in keywords}
    return normalized_result


def measure_multiprocessing(directory: str, keywords: List[str], num_processes=None):
    start = time.perf_counter()
    result = multiprocessing_search(directory, keywords, num_processes)
    end = time.perf_counter()
    print(f"[multiprocessing] Час виконання: {end - start:.4f} c")
    return result