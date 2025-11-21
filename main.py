# main.py
from threading_version import measure_threaded
from multiprocessing_version import measure_multiprocessing

KEYWORDS = ["python", "multiprocessing", "logging", "event", "thread"]
DIRECTORY = "data"

def normalize_result(result: dict, keywords: list[str]) -> dict:
    """
    Приводить результат до стабільного вигляду:
    - гарантує, що для кожного ключового слова є список (навіть якщо він пустий)
    - сортує списки шляхів, щоб порядок був однаковим
    """
    normalized = {}
    for kw in keywords:
        files = result.get(kw, [])
        # на всякий випадок прибираємо дублікати та сортуємо
        normalized[kw] = sorted(set(files))
    return normalized


def print_results(title: str, result: dict):
    print(f"\n=== {title} ===")
    for word in KEYWORDS:
        files = result.get(word, [])
        print(f"Слово '{word}':")
        if not files:
            print("  Не знайдено в жодному файлі.")
        else:
            for f in files:
                print(f"  - {f}")


if __name__ == "__main__":
    # багатопотокова версія
    threaded_raw = measure_threaded(DIRECTORY, KEYWORDS, num_threads=4)
    threaded_result = normalize_result(threaded_raw, KEYWORDS)
    print_results("Результати threading", threaded_result)

    # багатопроцесорна версія
    mp_raw = measure_multiprocessing(DIRECTORY, KEYWORDS)  # за замовчуванням cpu_count()
    mp_result = normalize_result(mp_raw, KEYWORDS)
    print_results("Результати multiprocessing", mp_result)

    # перевірка, що результати однакові
    if threaded_result == mp_result:
        print("\nРезультати збігаються для обох підходів.")
    else:
        print("\nУВАГА: результати відрізняються (перевір логіку).")