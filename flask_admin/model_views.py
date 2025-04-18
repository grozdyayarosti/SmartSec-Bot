from flask_admin.contrib.sqla import ModelView


# TODO решить с нумерацией
# TODO решить с сортировкой по буквам а не цифрам
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
