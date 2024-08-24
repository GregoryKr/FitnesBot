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


    def history_message(self) -> str:
        """
        Функция выводит информацию об истории тренировок
        :return: сообщение с данными о тренировке
        """
        type = 'Бег'
        return (f"Дата тренировки: {self.date}, \n"
                f"Тип тренировки: {type}, \n"
                f"дистанция: {self.distance} км, \n"
                f"потраченные калории: {self.spent_calories} \n")


class Swimming(Workout):
    __tablename__ = 'swimming'

    id = Column(Integer, ForeignKey('workout.id'), primary_key=True)
    action = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
    length_pool = Column(Float, nullable=False)
    count_pool = Column(Integer, nullable=False)
    speed = Column(Float, nullable=False)
    spent_calories = Column(Float, nullable=False)
    distance = Column(Float, nullable=False)

    workout = relationship('Workout', back_populates='swimming')

    __mapper_args__ = {
        'polymorphic_identity': 'swimming',
        'inherit_condition': id == Workout.id
    }
    def history_message(self) -> str:
        """
        Функция выводит информацию об истории тренировок
        :return: сообщение с данными о тренировке
        """
        type = 'Плавание'
        return (f"Дата тренировки: {self.date}, \n"
                f"Тип тренировки: {type}, \n"
                f"дистанция: {self.distance} км, \n"
                f"потраченные калории: {self.spent_calories} \n")

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
    def history_message(self) -> str:
        """
        Функция выводит информацию об истории тренировок
        :return: сообщение с данными о тренировке
        """
        type = 'Ходьба'
        return (f"Дата тренировки: {self.date}, \n"
                f"Тип тренировки: {type}, \n"
                f"дистанция: {self.distance} км, \n"
                f"потраченные калории: {self.spent_calories} \n")
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




