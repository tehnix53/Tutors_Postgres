from utility import random_six
from data import day_dict, goals_dict, \
    teachers

from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
from wtforms.validators import InputRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = "randomstring"
app.config["SQLALCHEMY_DATABASE_URI"] = \
    ("postgresql://postgres:postgres@127.0.0.1:5432/last")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

teachers_goals_association = db.Table(
    'teachers_goals', db.metadata,
    db.Column('teacher_id', db.Integer,
              db.ForeignKey('teachers.id')),
    db.Column('goal_id', db.Integer,
              db.ForeignKey('goals.id'))
)


class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    goal_type = db.Column(db.String, nullable=False)
    teachers = db.relationship("Teacher",
                               secondary=teachers_goals_association,
                               back_populates='goals')


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    name = db.Column(db.String, nullable=False)
    about = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    picture = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    goals = db.relationship("Goal",
                            secondary=teachers_goals_association,
                            back_populates='teachers')
    free = db.relationship("Shedule",
                           back_populates='teacher')
    booked = db.relationship("Booking",
                             back_populates='teacher')


class Shedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    teacher_id = db.Column(db.Integer,
                           db.ForeignKey('teachers.id'))
    teacher = db.relationship("Teacher",
                              back_populates='free')


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    day = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    teacher_id = db.Column(db.Integer,
                           db.ForeignKey('teachers.id'))
    teacher = db.relationship("Teacher",
                              back_populates='booked')


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)


db.create_all()

for t in teachers:
    tutor = Teacher(name=t['name'],
                    about=t['about'],
                    rating=t['rating'],
                    picture=t['picture'],
                    price=t['price'])
    db.session.add(tutor)

    for day, time in t['free'].items():
        for clock, status in time.items():
            shedule = Shedule(
                teacher=tutor,
                day=day,
                time=clock,
                status=status)

    for go in t['goals']:
        goal = Goal(goal_type=go)
        db.session.add(goal)
        goal.teachers.append(tutor)

db.session.commit()

tutors = db.session.query(Teacher)
shedule = db.session.query(Shedule)


class MyForm(FlaskForm):
    name = StringField('Вас зовут',
                       [InputRequired(message="Введите свое имя")])
    phone = StringField('Ваш телефон',
                        [InputRequired(message="Введите свой телефон!")])
    this_day = StringField([InputRequired()])


class RequestForm(FlaskForm):
    target = RadioField(choices=[('✈ Для путешествий', '✈ Для путешествий'),
                                 ("🏫 Для школы", "🏫 Для школы"),
                                 ("⚒ Для работы", "⚒ Для работы"),
                                 ("🚃 Для переезда", "🚃 Для переезда"),
                                 ('💻 для программирования', '💻 для программирования')])
    time = RadioField(choices=[('1-2 часа в неделю', '1-2 часа/нед.'),
                               ("3-5 часов в неделю", "3-5 часов/нед."),
                               ("5-7 часов в неделю", "5-7 часов/нед."),
                               ("7-10 часов в неделю", "7-10 часов/нед.")])
    name = StringField(InputRequired())
    phone = StringField(InputRequired())


@app.route('/test')
def testing_test():
    return render_template('test.html')


@app.route('/')
def teach_main():
    return render_template('index.html',
                           number=random_six(),
                           teach_list=tutors,
                           goals_dict=goals_dict)


@app.route('/all/')
def teach_all():
    return render_template('all.html',
                           tutors=tutors,
                           goals_dict=goals_dict)


@app.route('/profiles/<id>/')
def teach_himself(id):
    db.session.query(Teacher).get_or_404(id)
    return render_template('profile.html',
                           day_dict=day_dict,
                           teach_list=tutors,
                           id=id,
                           goals_dict=goals_dict,
                           shedule=shedule)


@app.route('/goals/<goal>/')
def teach_goals(goal):
    goal_teacher = Goal.query.filter(Goal.goal_type == goal).all()
    return render_template("goal.html",
                           goal=goal,
                           teach_list=tutors,
                           goals_dict=goals_dict,
                           goal_teacher=goal_teacher)


@app.route('/request/')
def teach_request():
    form = RequestForm()

    return render_template('request.html',
                           name=form.name,
                           time=form.time,
                           target=form.target,
                           phone=form.phone)


@app.route("/booking/<id>/<day>/<time>/")
def teach_booking(id, day, time):
    form = MyForm()
    return render_template('booking.html',
                           id=id,
                           teach_list=tutors,
                           day=day,
                           time=time,
                           name=form.name,
                           phone=form.phone,
                           this_day=form.this_day)


@app.route("/booking_done/<day>/<time>/<id>", methods=["POST"])
def teach_booking_done(day, time, id):
    form = MyForm()
    name = form.name.data
    phone = form.phone.data
    shedule_update = db.session.query(Shedule).filter(
        db.and_(Shedule.teacher_id == id,
                Shedule.day == day,
                Shedule.time == time)).first()
    shedule_update.status = False

    new_booking = Booking(name=name,
                          teacher_id=id,
                          phone=phone,
                          day=day,
                          time=time)
    db.session.add(new_booking)
    db.session.commit()
    return render_template('booking_done.html',
                           name=name,
                           phone=phone,
                           day=day,
                           time=time)


@app.route('/request_done/', methods=["POST"])
def request_success():
    form = RequestForm()
    name = form.name.data
    phone = form.phone.data
    time = form.time.data
    target = form.target.data
    new_request = Request(target=target,
                          time=time,
                          name=name,
                          phone=phone)
    db.session.add(new_request)
    db.session.commit()
    return render_template('request_done.html',
                           name=name,
                           phone=phone,
                           time=time,
                           target=target)


if __name__ == '__main__':
    app.run()
