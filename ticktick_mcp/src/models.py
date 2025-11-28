from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Project(BaseModel):
    id: str
    name: str
    color: Optional[str] = None
    closed: Optional[bool] = None
    group_id: Optional[str] = Field(default=None, alias="groupId")
    view_mode: Optional[str] = Field(default=None, alias="viewMode")
    kind: Optional[str] = None


class TaskItem(BaseModel):
    id: str
    status: int
    title: str
    sort_order: int = Field(alias="sortOrder")
    start_date: Optional[datetime] = Field(default=None, alias="startDate")
    is_all_day: Optional[bool] = Field(default=None, alias="isAllDay")
    time_zone: Optional[str] = Field(default=None, alias="timeZone")
    completed_time: Optional[datetime] = Field(default=None, alias="completedTime")


class Task(BaseModel):
    id: str
    is_all_day: Optional[bool] = Field(default=None, alias="isAllDay")
    project_id: str = Field(alias="projectId")
    title: str
    content: Optional[str] = None
    desc: Optional[str] = None
    time_zone: Optional[str] = Field(default=None, alias="timeZone")
    repeat_flag: Optional[str] = Field(default=None, alias="repeatFlag")
    start_date: Optional[datetime] = Field(default=None, alias="startDate")
    due_date: Optional[datetime] = Field(default=None, alias="dueDate")
    reminders: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    priority: Optional[int] = None
    status: Optional[int] = None
    completed_time: Optional[datetime] = Field(default=None, alias="completedTime")
    sort_order: Optional[int] = Field(default=None, alias="sortOrder")
    items: List[TaskItem] = Field(default_factory=list)


class Column(BaseModel):
    id: str
    project_id: str = Field(alias="projectId")
    name: str
    sort_order: int = Field(alias="sortOrder")


class ProjectData(BaseModel):
    project: Optional[Project] = None
    tasks: List[Task] = Field(default_factory=list)
    columns: List[Column] = Field(default_factory=list)
