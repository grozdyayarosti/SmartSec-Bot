from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Relationship


# TODO прописать Nullable-атрибуты
class BaseModel(DeclarativeBase): pass


class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String)
    is_completed = Column(Boolean)
    def __str__(self):
        return f"{self.login}"


class Question(BaseModel):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    text = Column(String)
    is_required = Column(Boolean)
    explanation = Column(String)
    def __str__(self):
        return f"{self.id}. {self.text}"


class Answer(BaseModel):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    text = Column(String)
    def __str__(self):
        return f"{self.id}. {self.text}"


class AnswerResult(BaseModel):
    __tablename__ = "question_answer_map"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    question = Relationship('Question')
    answer_id = Column(Integer, ForeignKey('answers.id'))
    answer = Relationship('Answer')
    is_correct = Column(Boolean)


class TestingResult(BaseModel):
    __tablename__ = "user_results"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    login = Relationship('User')
    question_id = Column(Integer, ForeignKey('questions.id'))
    question = Relationship('Question')
    is_correct_answer = Column(Boolean)
    answer_date = Column(Date)
