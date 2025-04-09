from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView

from models import User, Question, Answer, TestingResult, AnswerResult, AnswerResultsView
from smartsec_testing.constants import PG_USER, PG_PASSWORD, PG_HOST, PG_DBNAME, FLASK_SECRET_KEY

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
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

admin.add_view(ModelView(Question, db.session))
admin.add_view(ModelView(Answer, db.session))
admin.add_view(AnswerResultsView(AnswerResult, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(TestingResult, db.session))


if __name__ == '__main__':
    app.run()
