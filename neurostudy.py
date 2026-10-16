"""NeuroStudy — учебный планировщик задач для студентов.

Запуск:
    python neurostudy.py

Данные хранятся в tasks.json рядом с этим файлом.
Требуется Python 3.10+; сторонние библиотеки не нужны.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

DATA_FILE = Path(__file__).with_name("tasks.json")


@dataclass
class Task:
    title: str
    subject: str
    deadline: str
    hours: float
    difficulty: int
    done: bool = False

    def days_left(self) -> int:
        return (date.fromisoformat(self.deadline) - date.today()).days

    def priority(self) -> float:
        """Прозрачная эвристика приоритета, а не медицинская/научная оценка."""
        days = max(self.days_left(), 0)
        urgency = 10 / (days + 1)
        return round(urgency + 0.8 * self.difficulty + 0.3 * self.hours, 2)


def load_tasks(path: Path = DATA_FILE) -> list[Task]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Ожидался список задач.")
        return [Task(**item) for item in data]
    except (json.JSONDecodeError, TypeError, KeyError, ValueError) as exc:
        print(f"Предупреждение: не удалось загрузить задачи: {exc}")
        return []


def save_tasks(tasks: list[Task], path: Path = DATA_FILE) -> None:
    path.write_text(
        json.dumps([asdict(task) for task in tasks],
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def validate_task(title: str, subject: str, deadline: str,
                  hours: float, difficulty: int) -> None:
    if not title.strip():
        raise ValueError("Название задания не должно быть пустым.")
    if not subject.strip():
        raise ValueError("Название дисциплины не должно быть пустым.")
    try:
        parsed_deadline = date.fromisoformat(deadline)
    except ValueError as exc:
        raise ValueError("Дата должна быть в формате ГГГГ-ММ-ДД.") from exc
    if parsed_deadline < date.today():
        raise ValueError("Дедлайн не может быть в прошлом.")
    if hours <= 0:
        raise ValueError("Время выполнения должно быть больше нуля.")
    if not 1 <= difficulty <= 5:
        raise ValueError("Сложность должна быть от 1 до 5.")


def add_task_interactive(tasks: list[Task]) -> None:
    title = input("Название задания: ").strip()
    subject = input("Дисциплина: ").strip()
    deadline = input("Дедлайн (ГГГГ-ММ-ДД): ").strip()
    hours = float(input("Оценка времени в часах: "))
    difficulty = int(input("Сложность от 1 до 5: "))
    validate_task(title, subject, deadline, hours, difficulty)
    tasks.append(Task(title, subject, deadline, hours, difficulty))
    save_tasks(tasks)
    print("Задача добавлена и сохранена.")


def active_tasks_sorted(tasks: list[Task]) -> list[Task]:
    return sorted(
        (task for task in tasks if not task.done),
        key=lambda task: task.priority(),
        reverse=True,
    )


def show_tasks(tasks: list[Task]) -> None:
    active = active_tasks_sorted(tasks)
    if not active:
        print("Активных задач нет.")
        return

    print("\n--- План задач (по убыванию приоритета) ---")
    for number, task in enumerate(active, start=1):
        days = task.days_left()
        if days < 0:
            deadline_note = f"просрочено на {-days} дн."
        elif days == 0:
            deadline_note = "сдать сегодня"
        else:
            deadline_note = f"осталось {days} дн."
        print(
            f"{number}. [{task.subject}] {task.title}\n"
            f"   Дедлайн: {task.deadline} ({deadline_note}); "
            f"время: {task.hours:g} ч.; сложность: {task.difficulty}/5; "
            f"приоритет: {task.priority()}"
        )


def complete_task(tasks: list[Task]) -> None:
    active = active_tasks_sorted(tasks)
    if not active:
        print("Нет активных задач.")
        return
    show_tasks(tasks)
    try:
        number = int(input("Номер задачи, которую отметить выполненной: "))
    except ValueError:
        print("Введите целое число.")
        return
    if not 1 <= number <= len(active):
        print("Такого номера нет.")
        return
    selected = active[number - 1]
    selected.done = True
    save_tasks(tasks)
    print(f"Задача «{selected.title}» отмечена выполненной.")


def main() -> None:
    tasks = load_tasks()
    while True:
        print("\n=== NeuroStudy ===")
        print("1. Добавить учебную задачу")
        print("2. Показать план")
        print("3. Отметить задачу выполненной")
        print("4. Выход")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "1":
                add_task_interactive(tasks)
            elif choice == "2":
                show_tasks(tasks)
            elif choice == "3":
                complete_task(tasks)
            elif choice == "4":
                print("До встречи!")
                break
            else:
                print("Неизвестная команда. Выберите 1–4.")
        except (ValueError, OSError) as exc:
            print(f"Не удалось выполнить действие: {exc}")


if __name__ == "__main__":
    main()
