import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

from aiogram import types, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.settings import text as txt
from bot.kb import get_menu, choice_sport, register_user
from bot.states import RunState, DataState, WalkingState, SwimmingState
from bot.models import User, Base, Running, Swimming, Walking, Workout
from bot import calculations as calc


load_dotenv()

router = Router()

engine = create_engine(os.getenv('DB_URL'))
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    """
    Проверяет регистрацию пользователя, если пользователь зарегистрирован, направляет меню(клавиатуру).
    Если нет, то направляет меню для регистрации
    :param message:
    :return: None
    """
    user_id = message.from_user.id
    session = Session()
    user = session.query(User).filter_by(tg_id=user_id).first()
    if user:
        await message.answer(text=txt.menu_text, reply_markup=get_menu())
        session.close()
    else:
        await message.answer(text=txt.user_not_in_base, reply_markup=register_user())
        session.close()


@router.callback_query(F.data == "data")
async def registration_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Handler для запуска процесса регистрации
    :param call:  call от пользователя
    :param state: объект состояния
    :return: None
    """
    await state.set_state(DataState.age)
    await call.message.answer(text=txt.age)


@router.message(DataState.age)
async def age_handler(message: Message, state: FSMContext) -> None:
    """
    Проверяет корректность ввода возраста и устанавливает DataState.height
    :param message: команда от пользователя
    :param state: объект состояния
    :return: None
    """
    age = message.text
    r = range(0, 120)
    if age.isdigit() and float(age) in r:
        await state.update_data(age=age)
        await state.set_state(DataState.height)
        await message.answer(text=txt.height)
    else:
        await state.set_state(DataState.age)
        await message.answer(text=txt.incorrect_age_letters)


@router.message(DataState.height)
async def height_handler(message: Message, state: FSMContext) -> None:
    """
    Проверяет корректность ввода роста и устанавливает DataState.weight
    :param message: команда пользователя
    :param state: объект состояния
    :return: None
    """
    height = message.text
    r = range(50, 230)
    if height.isdigit() and float(height) in r:
        await state.update_data(height=height)
        await state.set_state(DataState.weight)
        await message.answer(text=txt.weight)
    else:
        await state.set_state(DataState.height)
        await message.answer(text=txt.incorrect_height)


@router.message(DataState.weight)
async def weight_handler(message: Message, state: FSMContext):
    """
    Сохраняет данные пользователя в базу данных
    :param message: команда пользователя
    :param state: объект состояния
    :return: клавиатуру с выбором спорта
    """
    weight = message.text
    r = range(15, 200)
    if weight.isdigit() and float(weight) in r:
        weight = float(weight)
        user_data = await state.get_data()
        user_age = user_data['age']
        user_height = user_data['height']
        user_id = message.from_user.id
        with Session() as session:
            new_user = User(tg_id=user_id, age=user_age, weight=weight, height=user_height)
            session.add(new_user)
            session.commit()
        await message.answer(text=txt.registration_text, reply_markup=choice_sport())
    else:
        await state.set_state(DataState.weight)
        await message.reply(text=txt.incorrect_weight_letters)


@router.callback_query(F.data == "info")
async def choice_sport_handler(call: types.CallbackQuery) -> None:
    """
    В ответ на нажатие кнопки добавить тренировку направляет меню с выбором спорта
    :param call: call от пользователя
    :return: None
    """
    await call.message.edit_text(text=txt.choice_text, reply_markup=choice_sport())


@router.callback_query(F.data.startswith("sport"))
async def sport_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Функция предлагает выбрать вид спорта
    :param call: call от пользователя
    :param state: объект состояния
    :return: None
    """
    sport_type = call.data.split('_')[1]
    sport_choice = {
        "running": state.set_state(RunState.actions),
        "walking": state.set_state(WalkingState.actions),
        "swimming": state.set_state(SwimmingState.actions)
    }
    await sport_choice[sport_type]
    await call.message.answer(text=txt.action_quantity)


def validate_digit_answer(func):
    async def wrapper(message: Message, state: FSMContext):
        numbers = message.text
        handler_state = await state.get_state()
        if numbers.isdigit():
            result = func(message, state)
            await result
        else:
            await message.answer(text=txt.incorrect_actions)
            await state.set_state(handler_state)
    return wrapper


@router.message(RunState.actions)
@validate_digit_answer
async def actions_handler_running(message: Message, state: FSMContext) -> None:
    """
    Функция сохраняет количество шагов пробежки
    :param message: команда пользователя
    :param state: объект состояния
    :return: None
    """
    steps_running = message.text
    # if steps_running.isdigit():
    await state.update_data(action=steps_running)
    await message.answer(text=txt.duration_running)
    await state.set_state(RunState.duration)


@router.message(RunState.duration)
async def running_handler_duration(message: Message, state: FSMContext) -> None:
    """
    Рассчитывает и показывает данные о тренировке по бегу (дистанция, расход калорий и т.д.)
    :param message: команда пользователя
    :param state: объект состояния
    :return: None, Данные о тренировке по бегу и reply_markup=get_menu()
    """
    running_duration = message.text
    if running_duration.isdigit():
        user_id = message.from_user.id
        with Session() as session:
            sportsman = session.query(User).filter_by(tg_id=user_id).first()
            user_weight = sportsman.weight

        user_data = await state.get_data()
        user_action = user_data['action']
        list_data = [float(user_action), float(running_duration), float(user_weight)]
        run_training = calc.read_package(workout_type='RUN', data=list_data)
        info = run_training.show_training_info()
        msg = info.get_message()
        run_distance = info.distance
        run_speed = info.speed
        spent_calories = info.calories

        with Session() as session:
            athlete = session.query(User).filter_by(tg_id=user_id).first()
            new_training = Running(action=user_action, duration=running_duration, user=athlete,
                                   distance=run_distance, speed=run_speed, spent_calories=spent_calories)
            session.add(new_training)
            session.commit()

        await message.answer(text=msg, parse_mode='HTML')
        await message.answer(text=txt.menu_text, reply_markup=get_menu())
    else:
        await message.answer(text=txt.incorrect_duration)
        await state.set_state(RunState.duration)


@router.message(WalkingState.actions)
@validate_digit_answer
async def actions_handler_walking(message: Message, state: FSMContext) -> None:
    """
    Сохраняет количество шагов во время прогулки
    :param message: команда пользователя
    :param state: объект состояния
    :return: None
    """
    steps_walking = message.text
    # if steps_walking.isdigit():
    await state.update_data(action=steps_walking)
    await message.answer(text=txt.duration_running)
    await state.set_state(WalkingState.duration)
    # else:
    #     await message.answer(text=txt.incorrect_actions)
    #     await state.set_state(WalkingState.actions)


@router.message(WalkingState.duration)
async def walking_handler_duration(message: Message, state: FSMContext) -> None:
    """
    Рассчитывает и показывает данные о тренировке/прогулке (дистанция, расход калорий и т.д.)
    :param message: команда пользователя
    :param state: объект состояния
    :return: None, данные о тренировке и reply_markup=get_menu()
    """
    walking_duration = message.text
    if walking_duration.isdigit():
        user_id = message.from_user.id
        with Session() as session:
            sportsman = session.query(User).filter_by(tg_id=user_id).first()
            user_weight = sportsman.weight
            user_height = sportsman.height

        user_data = await state.get_data()
        user_action = user_data['action']
        list_data = [float(user_action), float(walking_duration), float(user_weight), float(user_height)]
        walk = calc.read_package(workout_type='WLK', data=list_data)
        info = walk.show_training_info()
        msg = info.get_message()
        walk_distance = info.distance
        walk_speed = info.speed
        spent_calories = info.calories

        with Session() as session:
            athlete = session.query(User).filter_by(tg_id=user_id).first()
            new_training = Walking(action=user_action, duration=walking_duration, user=athlete,
                                   distance=walk_distance, speed=walk_speed, spent_calories=spent_calories)
            session.add(new_training)
            session.commit()
        await message.answer(text=msg, parse_mode='HTML')
        await message.answer(text=txt.menu_text, reply_markup=get_menu())
    else:
        await message.answer(text=txt.incorrect_duration)
        await state.set_state(WalkingState.duration)


@router.message(SwimmingState.actions)
@validate_digit_answer
async def actions_handler_swimming(message: Message, state: FSMContext) -> None:
    """
    Функция сохраняет количество гребков
    :param message: команда пользователя
    :param state: Объект состояния
    :return: None
    """
    steps_swimming = message.text
    # if steps_swimming.isdigit():
    await state.update_data(action=steps_swimming)
    await message.answer(text=txt.duration_running)
    await state.set_state(SwimmingState.duration)
    # else:
    #     await message.answer(text=txt.incorrect_actions)
    #     await state.set_state(SwimmingState.actions)


@router.message(SwimmingState.duration)
@validate_digit_answer
async def swimming_handler_duration(message: Message, state: FSMContext) -> None:
    """
    Функция сохраняет длительность плавания
    :param message: команда пользователя
    :param state: объект состояния
    :return: None
    """
    swimming_duration = message.text
    user_id = message.from_user.id
    # if swimming_duration.isdigit():
    await state.update_data(duration=swimming_duration)
    await message.answer(text=txt.length_pool)
    await state.set_state(SwimmingState.length_pool)
    # else:
    #     await message.answer(text=txt.incorrect_duration)
    #     await state.set_state(SwimmingState.duration)


@router.message(SwimmingState.length_pool)
@validate_digit_answer
async def insert_length_pool(message: Message, state: FSMContext) -> None:
    """
    Функция сохраняет длину бассейна
    :param message: команда пользователя
    :param state: объект состояния
    :return: None
    """
    length_pool = message.text
    # if length_pool.isdigit():
    await state.update_data(length_pool=length_pool)
    await message.answer(text=txt.count_pool)
    await state.set_state(SwimmingState.count_pool)
    # else:
    #     await message.asnwer(text=txt.incorrect_length_pool)
    #     await state.set_state(SwimmingState.length_pool)


@router.message(SwimmingState.count_pool)
async def insert_count_pool(message: Message, state: FSMContext) -> None:
    """
    Функция запрашивает всю необходимую информацию в БД и производит расчёт потраченных калорий
    за тренировку по плаванию
    :param message: команда пользователя
    :param state: объект состояния
    :return: None, сообщение о тренировке и потраченных калориях и возвращает меню с новой тренировкой или историей тренировок
    """
    count_pool = message.text
    if count_pool.isdigit():
        user_id = message.from_user.id
        with Session() as session:
            sportsman = session.query(User).filter_by(tg_id=user_id).first()
            user_weight = sportsman.weight

        user_data = await state.get_data()
        user_action = user_data['action']
        user_duration = user_data['duration']
        pool_length = user_data['length_pool']
        list_data = [float(user_action), float(user_duration), float(user_weight),
                     float(pool_length), float(count_pool)]
        swim_training = calc.read_package(workout_type='SWM', data=list_data)
        info = swim_training.show_training_info()
        msg = info.get_message()
        swim_distance = info.distance
        swim_speed = info.speed
        spent_calories = info.calories

        with Session() as session:
            athlete = session.query(User).filter_by(tg_id=user_id).first()
            new_swimming = Swimming(action=user_action, duration=user_duration, user=athlete,
                                    length_pool=pool_length, count_pool=count_pool,
                                    distance=swim_distance,
                                    spent_calories=spent_calories, speed=swim_speed)
            session.add(new_swimming)
            session.commit()
        await message.answer(text=msg, parse_mode='HTML')
        await message.answer(text=txt.menu_text, reply_markup=get_menu())
    else:
        await message.answer(text=txt.incorrect_count_pool)
        await state.set_state(SwimmingState.count_pool)


@router.callback_query(F.data == "history")
async def history_handler(call: types.CallbackQuery) -> None:
    """
    Функция для вывода истории тренировок
    :param call: call от пользователя
    :return: None
    """
    user_id = call.from_user.id
    with Session() as session:
        user = session.query(User).filter_by(tg_id=user_id).first()
        user_db_id = user.id
        history_1 = session.query(Workout).order_by(Workout.id.desc()).filter_by(user_id=user_db_id).limit(3).all()
        for training in history_1:
            info_about_training = training.history_message()
            await call.message.answer(text=info_about_training)
        await call.message.answer(text=txt.menu_text, reply_markup=get_menu())
