from flask import Flask
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView

from models import User, Question, Answer, UserResult, QuestionAnswerMap
from model_views import AnswerResultsView, TestingResultsView, UserView
from smartsec_testing.constants import PG_USER, PG_PASSWORD, PG_HOST, PG_DBNAME, FLASK_SECRET_KEY, FLASK_ADMIN_PORT


class StatsView(BaseView):
    @expose('/')
    def index(self):
        users_count = db.session.query(User).count()
        questions_count = db.session.query(Question).count()
        return self.render('admin/statistics.html',
                          users_count=users_count,
                          questions_count=questions_count)


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
admin.add_view(AnswerResultsView(QuestionAnswerMap, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(TestingResultsView(UserResult, db.session))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=FLASK_ADMIN_PORT)
