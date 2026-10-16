import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from neurostudy import Task, active_tasks_sorted, load_tasks, save_tasks, validate_task


class NeuroStudyTests(unittest.TestCase):
    def test_valid_task(self):
        validate_task(
            "Лабораторная", "Программирование",
            (date.today() + timedelta(days=2)).isoformat(),
            3.5, 4
        )

    def test_rejects_empty_title(self):
        with self.assertRaises(ValueError):
            validate_task(
                " ", "Математика",
                (date.today() + timedelta(days=2)).isoformat(),
                2, 3
            )

    def test_rejects_invalid_difficulty(self):
        with self.assertRaises(ValueError):
            validate_task(
                "Задача", "Математика",
                (date.today() + timedelta(days=2)).isoformat(),
                2, 6
            )

    def test_save_and_load(self):
        tasks = [Task(
            "Лабораторная", "Python",
            (date.today() + timedelta(days=3)).isoformat(),
            4, 3
        )]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.json"
            save_tasks(tasks, path)
            loaded = load_tasks(path)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].title, "Лабораторная")

    def test_completed_tasks_are_hidden_from_active_list(self):
        deadline = (date.today() + timedelta(days=1)).isoformat()
        tasks = [
            Task("Активная", "Python", deadline, 2, 2),
            Task("Готовая", "Математика", deadline, 1, 1, True),
        ]
        active = active_tasks_sorted(tasks)
        self.assertEqual([task.title for task in active], ["Активная"])


if __name__ == "__main__":
    unittest.main()
