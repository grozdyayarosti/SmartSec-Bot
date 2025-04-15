from flask_admin.contrib.sqla import ModelView
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Relationship

# TODO прописать Nullable-атрибуты
class AnswerResultsView(ModelView):
    column_list = ['question', 'answer', 'is_correct']  # Отображаемые в модели столбцы
    form_columns = ['question', 'answer', 'is_correct'] # Отображаемые в форме столбцы
    form_ajax_refs = {
        'question': {
            'fields': ['text', 'explanation'],   # Отображаемые в поиске столбцы
            # 'page_size': 10,                   # Пагинация
            'placeholder': 'Выберите вопрос...'  # Отображаемая в поиске подсказка
        },
        'answer': {
            'fields': ['text'],
            'placeholder': 'Выберите ответ...'
        }
    }
    column_sortable_list = (
        ('question', 'question.text'), ('answer', 'answer.text'), 'is_correct'
    )

class TestingResultsView(ModelView):
    column_list = ['login', 'question', 'is_correct_answer', 'answer_date']
    column_sortable_list = (
        'login', ('question', 'question.text'), 'is_correct_answer', 'answer_date'
    )
    can_create = False
    can_edit = False
    can_delete = False


class UserView(ModelView):
    column_list = ['id', 'login', 'is_completed']
    column_sortable_list = (
        'id', 'login', 'is_completed'
    )
    can_create = False
    can_edit = False
    can_delete = False

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
    __tablename__ = "answer_results"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    question = Relationship('Question')
    answer_id = Column(Integer, ForeignKey('answers.id'))
    answer = Relationship('Answer')
    is_correct = Column(Boolean)


class TestingResult(BaseModel):
    __tablename__ = "testing_results"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    login = Relationship('User')
    question_id = Column(Integer, ForeignKey('questions.id'))
    question = Relationship('Question')
    is_correct_answer = Column(Boolean)
    answer_date = Column(Date)
