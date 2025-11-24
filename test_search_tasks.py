import asyncio
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from ticktick_mcp.src import server
from ticktick_mcp.src.models import ProjectData, Project, Task


class FakeTickTickClient:
    def __init__(self) -> None:
        self.projects = [
            {"id": "project-1", "name": "Project 1"},
        ]
        self.tasks_by_project = {
            "project-1": [
                {
                    "id": "task-1",
                    "title": "Buy milk",
                    "projectId": "project-1",
                    "content": "Get almond milk and bread",
                    "startDate": "2024-01-01T03:00:00+0000",
                    "dueDate": "2024-01-02T03:00:00+0000",
                },
                {
                    "id": "task-2",
                    "title": "Write report",
                    "projectId": "project-1",
                    "content": "Prepare quarterly work report",
                    "startDate": "2024-01-03T03:00:00+0000",
                    "dueDate": "2024-01-04T03:00:00+0000",
                },
            ]
        }

    def get_projects(self):
        return self.projects

    def get_project_with_data(self, project_id: str):
        return {
            "project": {"id": project_id},
            "tasks": self.tasks_by_project.get(project_id, []),
        }

    def get_project_with_data_model(self, project_id: str) -> ProjectData:
        project = Project(id=project_id, name="Project 1")
        tasks = [
            Task.model_validate(task)
            for task in self.tasks_by_project.get(project_id, [])
        ]
        return ProjectData(project=project, tasks=tasks, columns=[])


class SearchTasksToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self._original_ticktick = server.ticktick
        server.ticktick = FakeTickTickClient()

    def tearDown(self) -> None:
        server.ticktick = self._original_ticktick

    def test_search_tasks_returns_matching_tasks(self) -> None:
        result = asyncio.run(server.search_tasks(["milk"]))

        self.assertIn("Found tasks:", result)
        self.assertIn("Buy milk", result)
        self.assertNotIn("Write report", result)

    def test_search_tasks_no_matching_tasks(self) -> None:
        result = asyncio.run(server.search_tasks(["nonexistent-keyword"]))

        self.assertEqual(
            "No tasks found matching the provided keywords.",
            result,
        )

    def test_get_tasks_returns_all_tasks_for_project_without_filters(self) -> None:
        result = asyncio.run(server.get_tasks(project_id="project-1"))

        self.assertIn("Buy milk", result)
        self.assertIn("Write report", result)

    def test_get_tasks_overdue_only(self) -> None:
        fixed_now = datetime(2024, 1, 3, tzinfo=timezone.utc)

        class FixedDateTime(datetime):
            @classmethod
            def now(cls, tz=None):
                return fixed_now

        with patch("ticktick_mcp.src.server.datetime", FixedDateTime):
            result = asyncio.run(
                server.get_tasks(project_id="project-1", overdue_only=True)
            )

        self.assertIn("Buy milk", result)
        self.assertNotIn("Write report", result)

    def test_get_tasks_due_in_next_7_days_only(self) -> None:
        fixed_now = datetime(2024, 1, 3, tzinfo=timezone.utc)

        class FixedDateTime(datetime):
            @classmethod
            def now(cls, tz=None):
                return fixed_now

        with patch("ticktick_mcp.src.server.datetime", FixedDateTime):
            result = asyncio.run(
                server.get_tasks(project_id="project-1", due_in_next_7_days=True)
            )

        self.assertIn("Write report", result)
        self.assertNotIn("Buy milk", result)

    def test_get_tasks_overdue_or_next_7_days(self) -> None:
        fixed_now = datetime(2024, 1, 3, tzinfo=timezone.utc)

        class FixedDateTime(datetime):
            @classmethod
            def now(cls, tz=None):
                return fixed_now

        with patch("ticktick_mcp.src.server.datetime", FixedDateTime):
            result = asyncio.run(
                server.get_tasks(
                    project_id="project-1",
                    overdue_only=True,
                    due_in_next_7_days=True,
                )
            )

        self.assertIn("Buy milk", result)
        self.assertIn("Write report", result)


if __name__ == "__main__":
    unittest.main()
