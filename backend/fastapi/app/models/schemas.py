from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class HealthResponse(BaseModel):
    status: str


class AssessmentSummary(BaseModel):
    assessment_type: str
    total_responses: int
    highest_score: Optional[int]
    average_score: Optional[float]
    latest_timestamp: Optional[str]


class AssessmentEntry(BaseModel):
    id: int
    total_score: int
    details: Dict[str, Any]
    timestamp: str


class AssessmentDetail(BaseModel):
    assessment_type: str
    entries: List[AssessmentEntry]


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: str


# Question schemas
class QuestionResponse(BaseModel):
    """Response schema for a single question"""
    id: int
    question_text: str
    category_id: Optional[int] = None
    difficulty: Optional[int] = None
    min_age: int = Field(default=0, description="Minimum age for this question")
    max_age: int = Field(default=120, description="Maximum age for this question")
    weight: float = Field(default=1.0, description="Question weight for scoring")
    tooltip: Optional[str] = Field(default=None, description="Helpful hint for the question")
    is_active: bool = Field(default=True, description="Whether the question is active")
    
    class Config:
        from_attributes = True


class QuestionSetResponse(BaseModel):
    """Response schema for a set of questions"""
    version: str = Field(description="Version identifier for the question set")
    total_questions: int = Field(description="Total number of questions in the set")
    questions: List[QuestionResponse] = Field(description="List of questions")
    age_range: Optional[dict] = Field(default=None, description="Age range filter applied")
    

class QuestionCategoryResponse(BaseModel):
    """Response schema for question category"""
    id: int
    name: str
    
    class Config:
        from_attributes = True


# Assessment schemas
class AssessmentResponse(BaseModel):
    """Response schema for a single assessment result"""
    id: int
    username: str
    total_score: int
    sentiment_score: Optional[float] = Field(default=0.0, description="NLTK sentiment analysis score")
    is_rushed: bool = Field(default=False, description="Indicates if assessment was rushed")
    is_inconsistent: bool = Field(default=False, description="Indicates inconsistent answers")
    age: Optional[int] = None
    detailed_age_group: Optional[str] = None
    timestamp: str
    
    class Config:
        from_attributes = True


class AssessmentDetailResponse(BaseModel):
    """Detailed assessment response with additional metadata"""
    id: int
    username: str
    total_score: int
    sentiment_score: Optional[float] = 0.0
    reflection_text: Optional[str] = None
    is_rushed: bool = False
    is_inconsistent: bool = False
    age: Optional[int] = None
    detailed_age_group: Optional[str] = None
    timestamp: str
    responses_count: Optional[int] = Field(default=0, description="Number of responses in this assessment")
    
    class Config:
        from_attributes = True


class AssessmentListResponse(BaseModel):
    """Response schema for listing assessments"""
    total: int = Field(description="Total number of assessments")
    assessments: List[AssessmentResponse] = Field(description="List of assessments")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=10, description="Number of items per page")


class AssessmentStatsResponse(BaseModel):
    """Statistical summary of assessments"""
    total_assessments: int
    average_score: float
    highest_score: int
    lowest_score: int
    average_sentiment: float
    age_group_distribution: dict = Field(description="Distribution of assessments by age group")
