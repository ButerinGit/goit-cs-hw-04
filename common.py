# common.py
from pathlib import Path
from typing import List


def get_text_files(directory: str) -> List[Path]:
    """
    Повертає список шляхів до всіх .txt файлів у вказаній директорії (рекурсивно).
    """
    base = Path(directory)
    return [p for p in base.rglob("*.txt") if p.is_file()]


def read_file_text(path: Path) -> str:
    """
    Безпечно читає текст з файлу, повертає пустий рядок, якщо сталася помилка.
    """
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        print(f"Помилка читання файлу {path}: {e}")
        return ""