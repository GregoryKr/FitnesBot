import sqlalchemy
# from sqlalchemy import Column, Integer, Float, String, DateTime, Table, ForeignKey
# from sqlalchemy.orm import declarative_base, relationship
#
#
#
# Base = declarative_base()
#
#
# association_table_running = Table('running_assoc_table', Base.metadata,
#                           Column('id', Integer, primary_key=True),
#                           Column('user_id', Integer, ForeignKey('user.user_id')),
#                           Column('run_training_id', Integer, ForeignKey('running.id'))
#                           )
#
#
# association_table_walking = Table('walking_assoc_table', Base.metadata,
#                                   Column('id', Integer, primary_key=True),
#                                   Column('user_id', Integer, ForeignKey('user.user_id')),
#                                   Column('walk_training_id', Integer, ForeignKey('walking.id'))
#                                   )
#
#
# association_table_swimming = Table('swim_assoc_table', Base.metadata,
#                                    Column('id', Integer, primary_key=True),
#                                    Column('user_id', Integer, ForeignKey('user.user_id')),
#                                    Column('swim_training_id', Integer, ForeignKey('swimming.id'))
#                                    )
# class User(Base):
#     __tablename__ = 'user'
#
#     user_id = Column(
#         Integer,
#         primary_key=True
#     )
#     username = Column(String(52), comment='tg Username')
#     age = Column(Float)
#     weight = Column(Float)
#     height = Column(Float)
#     tg_id = Column(Integer)
#     run = relationship('Running', secondary=association_table_running, back_populates='user')
#     walk = relationship('Walking', secondary=association_table_walking, back_populates='user')
#     swim = relationship('Swimming', secondary=association_table_swimming, back_populates='user')
#
#
# class Running(Base):
#     __tablename__ = 'running'
#     id = Column(Integer, primary_key=True)
#     action = Column(Integer)
#     duration = Column(Float)
#     date = Column(DateTime)
#     distance = Column(Float)
#     calories = Column(Float)
#     speed = Column(Float)
#     user = relationship('User', secondary=association_table_running, back_populates='run')
#
# class Walking(Base):
#     __tablename__ = 'walking'
#     id = Column(Integer, primary_key=True)
#     action = Column(Integer)
#     duration = Column(Float)
#     height = Column(Float)
#     date = Column(DateTime)
#     distance = Column(Float)
#     calories = Column(Float)
#     speed = Column(Float)
#     user = relationship('User', secondary=association_table_walking, back_populates='walk')
#
#
# class Swimming(Base):
#     __tablename__ = 'swimming'
#     id = Column(Integer, primary_key=True)
#     action = Column(Integer)
#     duration = Column(Float)
#     length_pool = Column(Float)
#     count_pool = Column(Integer)
#     date = Column(DateTime)
#     distance = Column(Float)
#     calories = Column(Float)
#     speed = Column(Float)
#     user = relationship('User', secondary=association_table_swimming, back_populates='swim')

import pytz
from datetime import datetime


from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship, declarative_base


moscow_time = pytz.timezone('Europe/Moscow')

Base = declarative_base()

class Workout(Base):
    __tablename__ = 'workout'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, default=datetime.now(moscow_time))
    type = Column(String(50))

    user = relationship('User', back_populates='workouts')

    __mapper_args__ = {
        'polymorphic_identity': 'workout',
        'polymorphic_on': type
    }


class Running(Workout):
    __tablename__ = 'running'

    id = Column(Integer, ForeignKey('workout.id'), primary_key=True)
    action = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
    speed = Column(Float, nullable=False)
    spent_calories = Column(Float, nullable=False)
    distance = Column(Float, nullable=False)

    workout = relationship('Workout', back_populates='running')

    __mapper_args__ = {
        'polymorphic_identity': 'running',
        'inherit_condition': id == Workout.id
    }


class Swimming(Workout):
    __tablename__ = 'swimming'

    id = Column(Integer, ForeignKey('workout.id'), primary_key=True)
    action = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
    len_pool = Column(Float, nullable=False)
    count_pool = Column(Integer, nullable=False)
    speed = Column(Float, nullable=False)
    spent_calories = Column(Float, nullable=False)
    distance = Column(Float, nullable=False)

    workout = relationship('Workout', back_populates='swimming')

    __mapper_args__ = {
        'polymorphic_identity': 'swimming',
        'inherit_condition': id == Workout.id
    }

class Walking(Workout):
    __tablename__ = 'walking'

    id = Column(Integer, ForeignKey('workout.id'), primary_key=True)
    action = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
    speed = Column(Float, nullable=False)
    spent_calories = Column(Float, nullable=False)
    distance = Column(Float, nullable=False)

    workout = relationship('Workout', back_populates='walking')

    __mapper_args__ = {
        'polymorphic_identity': 'walking',
        'inherit_condition': id == Workout.id
    }
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, nullable=False, unique=True)
    age = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    height = Column(Float)

    workouts = relationship('Workout', back_populates='user')

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}"

Workout.running = relationship('Running', back_populates='workout', uselist=False)
Workout.swimming = relationship('Swimming', back_populates='workout', uselist=False)
Workout.walking = relationship('Walking', back_populates='workout', uselist=False)

#дополнить таблицы Юзер (рост), дополнить все остальные таблицы(workout - вносим скорость, потраченные калории),
# добавить таблицу ходьбы,