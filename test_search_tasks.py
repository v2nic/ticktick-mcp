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
                    "tags": ["responsibility", "week1"],
                    "status": 0,  # Active
                },
                {
                    "id": "task-2",
                    "title": "Write report",
                    "projectId": "project-1",
                    "content": "Prepare quarterly work report",
                    "startDate": "2024-01-03T03:00:00+0000",
                    "dueDate": "2024-01-04T03:00:00+0000",
                    "tags": ["30Day"],
                    "status": 0,  # Active
                },
                {
                    "id": "task-3",
                    "title": "Meeting with team",
                    "projectId": "project-1",
                    "content": "Weekly sync",
                    "startDate": "2024-01-05T03:00:00+0000",
                    "dueDate": "2024-01-06T03:00:00+0000",
                    "tags": [],
                    "status": 0,  # Active
                },
                {
                    "id": "task-4",
                    "title": "Completed task",
                    "projectId": "project-1",
                    "content": "This task is done",
                    "startDate": "2024-01-07T03:00:00+0000",
                    "dueDate": "2024-01-08T03:00:00+0000",
                    "tags": ["week1"],
                    "status": 2,  # Completed
                },
                {
                    "id": "task-5",
                    "title": "Abandoned task",
                    "projectId": "project-1",
                    "content": "This task was abandoned",
                    "startDate": "2024-01-09T03:00:00+0000",
                    "dueDate": "2024-01-10T03:00:00+0000",
                    "tags": ["week1"],
                    "status": 5,  # Some other status (e.g., abandoned)
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

    def get_task(self, project_id: str, task_id: str):
        """Get a specific task by ID"""
        for task in self.tasks_by_project.get(project_id, []):
            if task.get('id') == task_id:
                return task
        return None


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

    def test_search_tasks_by_tag_only(self) -> None:
        """Test that searching by tags without keywords works"""
        result = asyncio.run(server.search_tasks(keywords=[], tags=["responsibility"]))

        self.assertIn("Found tasks:", result)
        self.assertIn("Buy milk", result)
        self.assertNotIn("Write report", result)
        self.assertNotIn("Meeting with team", result)

    def test_search_tasks_by_multiple_tags(self) -> None:
        """Test searching by multiple tags"""
        result = asyncio.run(server.search_tasks(keywords=[], tags=["week1", "30Day"]))

        self.assertIn("Found tasks:", result)
        self.assertIn("Buy milk", result)  # has week1 tag
        self.assertIn("Write report", result)  # has 30Day tag
        self.assertNotIn("Meeting with team", result)  # has no tags

    def test_search_tasks_by_nonexistent_tag(self) -> None:
        """Test searching for a tag that doesn't exist"""
        result = asyncio.run(server.search_tasks(keywords=[], tags=["nonexistent"]))

        self.assertEqual(
            "No tasks found matching the provided keywords.",
            result,
        )

    def test_search_tasks_with_keywords_and_tags(self) -> None:
        """Test searching with both keywords and tags"""
        result = asyncio.run(server.search_tasks(keywords=["milk"], tags=["responsibility"]))

        self.assertIn("Found tasks:", result)
        self.assertIn("Buy milk", result)
        self.assertNotIn("Write report", result)
        self.assertNotIn("Meeting with team", result)

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

    def test_search_tasks_empty_keywords_and_tags(self) -> None:
        """Test searching with empty keywords and tags - should return all tasks"""
        result = asyncio.run(server.search_tasks(keywords=[], tags=[]))

        self.assertIn("Found tasks:", result)
        self.assertIn("Buy milk", result)
        self.assertIn("Write report", result)
        self.assertIn("Meeting with team", result)

    def test_search_tasks_case_insensitive_tag_matching(self) -> None:
        """Test that tag matching is case insensitive"""
        result = asyncio.run(server.search_tasks(keywords=[], tags=["RESPONSIBILITY"]))

        self.assertIn("Found tasks:", result)
        self.assertIn("Buy milk", result)
        self.assertNotIn("Write report", result)

    def test_search_tasks_exact_tag_matching(self) -> None:
        """Test that tag matching requires exact match (not partial)"""
        result = asyncio.run(server.search_tasks(keywords=[], tags=["week"]))

        self.assertEqual(
            "No tasks found matching the provided keywords.",
            result,
        )

    def test_search_tasks_exact_tag_match_works(self) -> None:
        """Test that exact tag matching works"""
        result = asyncio.run(server.search_tasks(keywords=[], tags=["week1"]))

        self.assertIn("Found tasks:", result)
        self.assertIn("Buy milk", result)  # has "week1" tag
        self.assertNotIn("Write report", result)

    def test_search_tasks_status_filter_active(self) -> None:
        """Test searching with status='active' filter"""
        result = asyncio.run(server.search_tasks(keywords=[], status="active"))

        self.assertIn("Found tasks:", result)
        self.assertIn("Buy milk", result)  # active task
        self.assertIn("Write report", result)  # active task
        self.assertIn("Meeting with team", result)  # active task

    def test_search_tasks_status_filter_completed(self) -> None:
        """Test searching with status='completed' filter"""
        result = asyncio.run(server.search_tasks(keywords=[], status="completed"))

        # Should return the completed task
        self.assertIn("Found tasks:", result)
        self.assertIn("Completed task", result)  # completed task
        self.assertNotIn("Buy milk", result)  # active task
        self.assertNotIn("Write report", result)  # active task

    def test_search_tasks_status_filter_with_tags(self) -> None:
        """Test searching with both status and tags"""
        result = asyncio.run(server.search_tasks(keywords=[], tags=["30Day"], status="active"))

        self.assertIn("Found tasks:", result)
        self.assertIn("Write report", result)  # has "30Day" tag and is active
        self.assertNotIn("Buy milk", result)  # doesn't have "30Day" tag

    def test_search_tasks_default_status_active(self) -> None:
        """Test that default behavior returns only active tasks"""
        result = asyncio.run(server.search_tasks(keywords=[]))

        self.assertIn("Found tasks:", result)
        self.assertIn("Buy milk", result)  # active task
        self.assertIn("Write report", result)  # active task
        self.assertIn("Meeting with team", result)  # active task

    def test_task_status_display(self) -> None:
        """Test that different task statuses are displayed correctly"""
        result = asyncio.run(server.get_task(project_id="project-1", task_id="task-5"))

        self.assertIn("Abandoned task", result)
        self.assertIn("Status: Unknown (5)", result)  # Should show unknown status value


if __name__ == "__main__":
    unittest.main()
