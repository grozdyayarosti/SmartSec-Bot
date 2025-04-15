from flask import Flask
from flask_admin import Admin, AdminIndexView, expose
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView

from models import User, Question, Answer, TestingResult, AnswerResult
from model_views import AnswerResultsView, TestingResultsView, UserView
from smartsec_testing.constants import PG_USER, PG_PASSWORD, PG_HOST, PG_DBNAME, FLASK_SECRET_KEY


class StatsView(AdminIndexView):
    @expose('/statistics')
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
# Конфигурация БД (замените на свои параметры)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/{PG_DBNAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
# app.config['FLASK_ADMIN_FLUID_DEBUG'] = True  # Расширенная отладка Flask-Admin
# app.config['DEBUG'] = True  # Детальные ошибки в браузере
# TODO вынести db в models.py
db = SQLAlchemy(app)
# engine = create_engine(f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/{PG_DBNAME}')
# metadata = MetaData(bind=engine)

# Настройка админки
admin = Admin(app,
              name='Admin Panel',
              template_mode='bootstrap3',
              index_view=ManualView())

# admin.add_view(StatsView(db.session))
admin.add_view(ModelView(Question, db.session))
admin.add_view(ModelView(Answer, db.session))
admin.add_view(AnswerResultsView(AnswerResult, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(TestingResultsView(TestingResult, db.session))


if __name__ == '__main__':
    app.run()
