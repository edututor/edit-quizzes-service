from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AnswerSchema(BaseModel):
    id: Optional[int] = None
    answer_text: str
    is_correct_answer: bool

class QuestionSchema(BaseModel):
    id: Optional[int] = None
    question_text: str
    hint: str
    answers: List[AnswerSchema]

class EditQuizRequest(BaseModel):
    id: int
    title: str
    document_name: str
    created_at: Optional[datetime] = None
    questions: List[QuestionSchema]

class QuizSchema(BaseModel):
    quiz_name: str
    questions: List[QuestionSchema]