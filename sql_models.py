from app import app
from data import teachers
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)
teachers_goals_association = db.Table('teachers_goals', db.metadata,
                                      db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id')),
                                      db.Column('goal_id', db.Integer, db.ForeignKey('goals.id'))
                                      )


class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    goal_type = db.Column(db.String, nullable=False)
    teachers = db.relationship("Teacher", secondary=teachers_goals_association,
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
    goals = db.relationship("Goal", secondary=teachers_goals_association,
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


# db.create_all()

for t in teachers:
    tutor = Teacher(name=t['name'], about=t['about'], rating=t['rating'],
                    picture=t['picture'], price=t['price'])
    db.session.add(tutor)

    for day, time in t['free'].items():
        for clock, status in time.items():
            # print(day, clock, status)
            shedule = Shedule(teacher=tutor, day=day, time=clock, status=status)

    for go in t['goals']:
        goal = Goal(goal_type=go)
        db.session.add(goal)
        goal.teachers.append(tutor)

# db.session.commit()
tutors = db.session.query(Teacher)
shedule = db.session.query(Shedule)












