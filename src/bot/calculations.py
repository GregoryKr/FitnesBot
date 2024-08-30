
class Training:
    M_IN_KM = 1000

    def __init__(self, action: int, duration: float, weight: float):
        self.action = action
        self.duration = duration
        self.weight = weight

    def get_distance(self) -> float:
        """
        Расчёт дистанции, которую преодолел пользователь за тренировку
        :return: дистанция
        """
        distance = self.action * self.LEN_STEP / self.M_IN_KM
        return round(distance, 3)

    def get_mean_speed(self) -> float:
        """
        Расчёт средней скорости движения во время тренировки
        :return: средняя скорость во время тренировки
        """
        speed = self.get_distance() / self.duration
        return speed

    def get_spent_calories(self) -> float:
        """расчёт количества калорий за тренировку
         у каждого потомка свой """
        pass

    def show_training_info(self):
        """
        создание объекта сообщения(info) о результатах тренировки
        :return: объект сообщения info для дальнейшего вывода на экран
        """
        training_type = self.__class__.__name__
        info = InfoMessage(training_type=training_type,
                           duration=self.duration,
                           distance=self.get_distance(),
                           speed=self.get_mean_speed(),
                           calories=self.get_spent_calories())
        return info


class Walking:
    LEN_STEP = 0.65


class Running(Training, Walking):
    def __init__(self, action: int, duration: float, weight: float):
        super().__init__(action=action, duration=duration, weight=weight)

    def get_spent_calories(self) -> float:
        """рассчёт количества калорий за тренировку"""
        CALORIES_MEAN_SPEED_MULTIPLIER = 18
        CALORIES_MEAN_SPEED_SHIFT = 1.79
        mean_speed = self.get_mean_speed()
        part_of_formula = CALORIES_MEAN_SPEED_MULTIPLIER * mean_speed + CALORIES_MEAN_SPEED_SHIFT
        spent_calories = part_of_formula*self.weight/self.M_IN_KM * self.duration*60
        return round(spent_calories, 3)


class SportsWalking(Training, Walking):
    def __init__(self, action: int, duration: float, weight: float, height: float):
        self.height = height
        super().__init__(action=action, duration=duration, weight=weight)

    def get_spent_calories(self) -> float:
        """расчёт количества калорий за тренировку"""
        KOEF_1 = 0.035
        KOEF_2 = 0.029
        mean_speed = self.get_mean_speed()
        part_of_formula = KOEF_1 * self.weight + ((mean_speed * self.M_IN_KM / 60 * 60) ** 2 / self.height)
        spent_calories = ((part_of_formula * KOEF_2 * self.weight) * self.duration*60)
        return round(spent_calories, 3)


class Swimming(Training):
    LEN_STEP = 1.38

    def __init__(self, action: int, duration: float, weight: float, length_pool: float, count_pool: int):
        self.length_pool = length_pool
        self.count_pool = count_pool
        super().__init__(action=action, duration=duration, weight=weight)

    def get_mean_speed(self) -> float:
        """
        Расчёт средней скорости движения во время тренировки
        :return: средняя скорость во время тренировки
        """
        speed = ((self.length_pool*self.count_pool)/self.M_IN_KM)/self.duration
        return speed

    def get_spent_calories(self) -> float:
        """рассчёт количества калорий за тренировку"""
        CALORIES_MEAN_SPEED_MULTIPLIER = 18
        CALORIES_MEAN_SPEED_SHIFT = 1.79
        mean_speed = self.get_mean_speed()
        part_of_formula = CALORIES_MEAN_SPEED_MULTIPLIER*mean_speed+CALORIES_MEAN_SPEED_SHIFT
        spent_calories = part_of_formula*self.weight/self.M_IN_KM*self.duration*60
        return round(spent_calories, 3)


class InfoMessage:
    def __init__(self, training_type: str, duration: float, distance: float, speed: float, calories: float):
        self.training_type = training_type
        self.duration = duration
        self.distance = distance
        self.speed = speed
        self.calories = calories

    def get_message(self) -> str:
        """
        Функция выводит информацию о пройденной тренировке
        на экран(печатает данные из экземпляра класса info)
        :return: сообщение с данными о тренировке
        """
        if self.training_type == "Running":
            training_type = 'Бег'
        elif self.training_type == 'Swimming':
            training_type = 'Плавание'
        elif self.training_type == 'SportsWalking':
            training_type = 'Ходьба'
        else:
            training_type = 'Тренировка не найдена'

        return (f"Тип тренировки: {training_type}, \n"
                f"длительность: {self.duration} ч., \n"
                f"дистанция: {self.distance} км, \n"
                f"потраченные калории: {self.calories}, \n"
                f"средняя скорость: {self.speed} км/ч")


def read_package(workout_type: str, data: list) -> Training:
    """
    Функция создаёт экземпляр класса training, из словаря выбирает необходимый класс по аббревиатуре и распаковыввает
    данные по каждой тренировке, сохраняет в экземпляр класса
    :param workout_type: тип тренировки, ключ в словаре
    :param data: показатели по каждой тренировки
    :return: экземпляр класса training
    """
    sport_choice = {
        'SWM': Swimming,
        'RUN': Running,
        'WLK': SportsWalking
    }

    sport = sport_choice[workout_type]
    training = sport(*data)
    return training


def main(training: Training) -> None:
    """ Функция запускает код, методы для вывода информации по тренировке
    :param training: экземпляр класса training
    :return: None
    """
    info = training.show_training_info()
    print(info.get_message())


if __name__ == '__main__':
    packages = [
        ('SWM', [720, 1, 80, 25, 40]),
        ('RUN', [15000, 1, 75]),
        ('WLK', [9000, 1, 75, 180])
    ]

    for workout_type, data in packages:
        training = read_package(workout_type, data)
        main(training)
