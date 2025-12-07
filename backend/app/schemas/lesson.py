from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class LessonBase(BaseModel):
    theory_text: Optional[str] = None
    reading_text: Optional[str] = None
    speaking_text: Optional[str] = None
    lesson_test_json: Optional[Dict[str, Any]] = None
    lesson_notes: Optional[str] = None
    results_json: Optional[Dict[str, Any]] = None
    is_access: bool = False
    is_ended: bool = False

class LessonCreate(LessonBase):
    pass

class LessonUpdate(LessonBase):
    pass

class LessonResponse(LessonBase):
    lesson_id: int
    
    class Config:
        from_attributes = True

class LessonProgress(BaseModel):
    theory_completed: bool = False
    reading_completed: bool = False
    speaking_completed: bool = False
    test_completed: bool = False
    test_score: int = 0
    details: Optional[Dict[str, Any]] = None

class CourseLessonsInfo(BaseModel):
    lessons: List[Dict[str, Any]]
    graph: Optional[Dict[str, Any]] = None
    user_course_id: Optional[int] = None
    knowledge_gaps: Optional[str] = None

class LessonTestSubmit(BaseModel):
    answers: List[Dict[str, Any]]
    score: int

class LessonContentUpdate(BaseModel):
    content: str
    content_type: str  # "theory", "reading", "speaking", "test", "notes"
    is_access: Optional[bool] = None
    is_ended: Optional[bool] = None

class LessonProgressUpdate(BaseModel):
    progress_type: str  # "theory", "reading", "speaking", "test"
    data: Dict[str, Any]