from flask import Flask
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import func, case, desc, text

from models import User, Question, Answer, UserResult, QuestionAnswerMap
from model_views import QuestionAnswerMapView, UserResultsView, UserView
from constants import PG_USER, PG_PASSWORD, PG_HOST, PG_DBNAME, FLASK_SECRET_KEY, FLASK_ADMIN_PORT


class StatsView(BaseView):
    @expose('/')
    def index(self):
        statistics_dict = get_statistics_values()
        return self.render('admin/statistics.html',
                          users_count=statistics_dict["users_count"],
                          users_who_not_passed_testing=statistics_dict["users_who_not_passed_testing_str"],
                          questions_count=statistics_dict["questions_count"],
                          hardest_question=statistics_dict["hardest_question"],
                          easiest_question=statistics_dict["easiest_question"])

def get_statistics_values():
    users_count = db.session.query(User).count()
    users_who_not_passed_testing = db.session.query(User.login).filter(~User.is_completed).all()
    users_who_not_passed_testing_str = ', '.join(l[0] for l in users_who_not_passed_testing)
    questions_count = db.session.query(Question).count()

    def get_easiest_or_hardest_question():
        question_query = db.session.query(
            UserResult.question_id,
            func.count(case((UserResult.is_correct_answer == True, 1))).label('correct_count')
            ).group_by(UserResult.question_id
            ).with_entities(UserResult.question_id)

        hardest_question_id = question_query.order_by(desc(func.count(case((UserResult.is_correct_answer == True, 1))))
                                                      ).limit(1).scalar()
        hardest_question_obj = db.session.query(Question).filter(Question.id == hardest_question_id).scalar()
        hardest_question_str = hardest_question_obj.text if not None else '...'

        easiest_question_id = question_query.order_by(func.count(case((UserResult.is_correct_answer == True, 1)))
                                                      ).limit(1).scalar()
        easiest_question_obj = db.session.query(Question).filter(Question.id == easiest_question_id).scalar()
        easiest_question_text = easiest_question_obj.text if not None else '...'

        return hardest_question_str, easiest_question_text

    hardest_question, easiest_question = get_easiest_or_hardest_question()
    return {"users_count": users_count,
            "users_who_not_passed_testing_str": users_who_not_passed_testing_str,
            "questions_count": questions_count,
            "hardest_question": hardest_question,
            "easiest_question": easiest_question}


class ManualView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/manual.html')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/{PG_DBNAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
# app.config['FLASK_ADMIN_FLUID_DEBUG'] = True  # Расширенная отладка Flask-Admin
# app.config['DEBUG'] = True  # Детальные ошибки в браузере
# TODO вынести db в models.py
db = SQLAlchemy(app)

admin = Admin(app,
              name='Admin Panel',
              template_mode='bootstrap3',
              index_view=ManualView(name='Home'))

admin.add_view(StatsView(name='Statistics', endpoint='statistics'))
admin.add_view(ModelView(Question, db.session))
admin.add_view(ModelView(Answer, db.session))
admin.add_view(QuestionAnswerMapView(QuestionAnswerMap, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(UserResultsView(UserResult, db.session))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=FLASK_ADMIN_PORT)
