from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class TestQuestionBase(BaseModel):
    """Базовая схема для вопроса теста"""
    question_id: str
    type: str  # "short_answer", "single_choice", "multiple_choice", "gaps_choice"
    question: str
    max_score: Optional[int] = 1

class ShortAnswerQuestion(TestQuestionBase):
    type: str = "short_answer"
    max_length: int
    correct_answer: str

class SingleChoiceQuestion(TestQuestionBase):
    type: str = "single_choice"
    options: List[str]
    correct_answer: int  # индекс правильного ответа

class MultipleChoiceQuestion(TestQuestionBase):
    type: str = "multiple_choice"
    options: List[str]
    correct_answers: List[int]  # индексы правильных ответов

class GapChoice(BaseModel):
    """Схема для одного пропуска в gaps_choice"""
    gap_id: int
    options: List[str]
    correct_answer: int

class GapsChoiceQuestion(TestQuestionBase):
    type: str = "gaps_choice"
    gaps: List[GapChoice]

# Объединенная схема для всех типов вопросов
TestQuestion = ShortAnswerQuestion | SingleChoiceQuestion | MultipleChoiceQuestion | GapsChoiceQuestion

class TestGenerationRequest(BaseModel):
    """Схема для запроса генерации теста с замечаниями"""
    feedback: Optional[str] = None

class GeneratedTestResponse(BaseModel):
    """Схема для ответа с сгенерированным тестом"""
    questions: List[Dict[str, Any]]
    generation_id: str
    generated_at: datetime
    feedback_used: Optional[str] = None

class TestFinalizationRequest(BaseModel):
    """Схема для финализации теста"""
    finalize: bool = True

class TestStatusResponse(BaseModel):
    """Схема для проверки статуса теста"""
    course_id: int
    is_test_generated: bool
    is_test_finalized: bool
    last_generation_time: Optional[datetime] = None
    questions_count: int = 0
    has_feedback: bool = False