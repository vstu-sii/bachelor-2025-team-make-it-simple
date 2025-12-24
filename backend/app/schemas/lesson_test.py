from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class LessonTestQuestionBase(BaseModel):
    """Базовая схема для вопроса теста урока"""
    question_id: str
    type: str  # "short_answer", "single_choice", "multiple_choice", "gaps_choice"
    question: str
    max_score: Optional[int] = 1

class ShortAnswerQuestion(LessonTestQuestionBase):
    type: str = "short_answer"
    max_length: int
    correct_answer: str

class SingleChoiceQuestion(LessonTestQuestionBase):
    type: str = "single_choice"
    options: List[str]
    correct_answer: int  # индекс правильного ответа

class MultipleChoiceQuestion(LessonTestQuestionBase):
    type: str = "multiple_choice"
    options: List[str]
    correct_answers: List[int]  # индексы правильных ответов

class GapChoice(BaseModel):
    """Схема для одного пропуска в gaps_choice"""
    gap_id: int
    options: List[str]
    correct_answer: int

class GapsChoiceQuestion(LessonTestQuestionBase):
    type: str = "gaps_choice"
    gaps: List[GapChoice]

# Объединенная схема для всех типов вопросов
LessonTestQuestion = ShortAnswerQuestion | SingleChoiceQuestion | MultipleChoiceQuestion | GapsChoiceQuestion

class LessonTestGenerationRequest(BaseModel):
    """Схема для запроса генерации теста урока с замечаниями"""
    feedback: Optional[str] = None

class GeneratedLessonTestResponse(BaseModel):
    """Схема для ответа с сгенерированным тестом урока"""
    questions: List[Dict[str, Any]]
    generation_id: str
    generated_at: datetime
    feedback_used: Optional[str] = None

class LessonTestFinalizationRequest(BaseModel):
    """Схема для финализации теста урока"""
    finalize: bool = True

class LessonTestStatusResponse(BaseModel):
    """Схема для проверки статуса теста урока"""
    lesson_id: int
    is_test_generated: bool
    is_test_finalized: bool
    last_generation_time: Optional[datetime] = None
    questions_count: int = 0
    has_feedback: bool = False

class StudentTestSubmission(BaseModel):
    """Схема для отправки результатов теста учеником"""
    tasks: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None

class StudentTestResults(BaseModel):
    """Схема для результатов теста ученика"""
    score: int
    max_score: int
    percentage: float
    completed_at: datetime
    detailed_results: List[Dict[str, Any]]

class LessonTestEvaluation(BaseModel):
    """Схема для оценки результатов теста"""
    lesson_id: int
    student_id: int
    results: StudentTestResults
    recommendations: Optional[List[str]] = None
    evaluated_at: datetime