from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aiogram import types, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode

from bot.settings import text as txt  #menu_text, choice_text
from bot.kb import get_menu, choice_sport, register_user
from bot.states import RunState, DataState, WalkingState, SwimmingState
from bot.models import User, Base, Running, Swimming, Walking, Workout
from bot import calculations as calc


router = Router()

engine = create_engine('postgresql://postgres:03121981@localhost:5432/dg_tg_bot')

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


@router.message(Command("start"))
async def start_handler(message: Message):
    """
    Проверяет регистрацию пользователя, если пользователь зарегистрирован, направляет меню(клавиатуру).
    Если нет, то направляет меню для регистрации
    :param message:
    :return:
    """
    user_id = message.from_user.id
    session = Session()
    user_1 = session.query(User).filter_by(tg_id=user_id).first()
    if user_1:
        await message.answer(text=txt.menu_text, reply_markup=get_menu())
        session.close()
    else:
        await message.answer(text=txt.user_not_in_base, reply_markup=register_user())
        session.close()


@router.callback_query(F.data == "data")
async def data_handler(call: types.CallbackQuery, state: FSMContext):
    """
    В ответ на нажатие кнопки о регистрации устанавливает DataStat.age
    :param call:
    :param state:
    :return: DataState.age
    """
    await state.set_state(DataState.age)
    await call.message.answer(text=txt.age)


@router.message(DataState.age)
async def age_handler(message: Message, state: FSMContext):
    """
    Проверяет корректность ввода возраста и устанавливает DataState.hieght
    :param message:
    :param state:
    :return: DataState.hieght
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
async def height_handler(message: Message, state: FSMContext):
    """
    Проверяет корректность ввода роста и устанавливает DataState.weight
    :param message:
    :param state:
    :return: DataState.weight
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
    :param message:
    :param state:
    :return: клавиатуру с выбором спорта
    """
    weight = message.text  # check if weight is written correctly
    r = range(15, 200)
    if weight.isdigit() and float(weight) in r:
        weight = float(weight)
        user_id = message.from_user.id  # надо сначала сохранить user
        user_data = await state.get_data()
        user_age = user_data['age']
        user_height = user_data['height']
        with Session() as session:
            new_user = User(tg_id=user_id, age=user_age, weight=weight, height=user_height)
            session.add(new_user)
            session.commit()
        await message.answer(text=txt.registration_text, reply_markup=choice_sport())
    else:
        await state.set_state(DataState.weight)
        await message.reply(text=txt.incorrect_weight_letters)


@router.callback_query(F.data == "info")
async def choice_sport_handler(call: types.CallbackQuery):
    """
    В ответ на нажатие кнопки добавить тренировку направляет меню с выбором спорта
    :param call:
    :return: reply_markup=choice_sport()
    """
    await call.message.edit_text(text=txt.choice_text, reply_markup=choice_sport())


@router.callback_query(F.data == "history")
async def history_handler(call: types.CallbackQuery):
    """
    Функция для вывода истории тренировок
    :param call:
    :return: история и reply_markup=get_menu()
    """
    user_id = call.from_user.id
    # print(user_id)
    with Session() as session:
        user_1 = session.query(User).filter_by(tg_id=user_id).first()
        id_1 = user_1.id
        # print(id_1)
        history_1 = session.query(Workout).filter_by(user_id=id_1).limit(3).all()
        print(history_1)
        for training in history_1:
            info_about_training = training.history_message()
            await call.message.answer(text=info_about_training)
        await call.message.answer(text=txt.menu_text, reply_markup=get_menu())


@router.callback_query(F.data.startswith("sport"))
async def sport_handler(call: types.CallbackQuery, state: FSMContext):
    """
    Функция предлагает выбрать вид спорта
    :param call:
    :param state:
    :return: RunState.actions или WalkingState.actions или SwimmingState.actions
    """
    sport_type = call.data.split('_')[1] # второе слово из call тип тренировки
    await call.message.answer(text=txt.action_quantity)
    if sport_type == "running":
        await state.set_state(RunState.actions)
    if sport_type == "walking":
        await state.set_state(WalkingState.actions)
    if sport_type == "swimming":
        await state.set_state(SwimmingState.actions)


@router.message(RunState.actions)
async def actions_handler_running(message: Message, state: FSMContext):
    """
    Функция сохраняет количество шагов пробежки
    :param message:
    :param state:
    :return: RunState.duration
    """
    steps_running = message.text
    if steps_running.isdigit():
        await state.update_data(action=steps_running)
        await message.answer(text=txt.duration_running)
        await state.set_state(RunState.duration)
    else:
        await message.answer(text=txt.incorrect_actions)
        await state.set_state(RunState.actions)


@router.message(RunState.duration)
async def running_handler_duration(message: Message, state: FSMContext):
    """
    Рассчитывает и показывает данные о тренировке по бегу (дистанция, расход калорий и т.д.)
    :param message:
    :param state:
    :return: Данные о тренировке по бегу и reply_markup=get_menu()
    """
    running_duration = message.text
    user_id = message.from_user.id
    if running_duration.isdigit():
        user_data = await state.get_data()
        user_action = user_data['action']
        with Session() as session:
            user_1 = session.query(User).filter_by(tg_id=user_id).first()
            user_weight = user_1.weight
        list_data = [float(user_action), float(running_duration), float(user_weight)]
        run_1 = calc.read_package(workout_type='RUN', data=list_data)
        info = run_1.show_training_info()
        msg = info.get_message()
        run_distance = info.distance
        run_speed = info.speed
        spent_calories = info.calories
        with Session() as session:
            user_1 = session.query(User).filter_by(tg_id=user_id).first()
            new_training = Running(action=user_action, duration=running_duration, user=user_1,
                                   distance=run_distance, speed=run_speed, spent_calories=spent_calories)
            session.add(new_training)
            session.commit()

        await message.answer(text=msg, parse_mode='HTML')
        await message.answer(text=txt.menu_text, reply_markup=get_menu())
    else:
        await message.answer(text=txt.incorrect_duration)
        await state.set_state(RunState.duration)


@router.message(WalkingState.actions)
async def actions_handler_walking(message: Message, state: FSMContext):
    """
    Сохраняет количество шагов во время прогулки
    :param message:
    :param state:
    :return: WalkingState.duration
    """
    steps_walking = message.text
    if steps_walking.isdigit():
        await state.update_data(action=steps_walking)
        await message.answer(text=txt.duration_running)
        await state.set_state(WalkingState.duration)
    else:
        await message.answer(text=txt.incorrect_actions)
        await state.set_state(WalkingState.actions)


@router.message(WalkingState.duration)
async def walking_handler_duration(message: Message, state: FSMContext):
    """
    Рассчитывает и показывает данные о тренировке/прогулке (дистанция, расход калорий и т.д.)
    :param message:
    :param state:
    :return: данные о тренировке и reply_markup=get_menu()
    """
    walking_duration = message.text
    user_id = message.from_user.id
    if walking_duration.isdigit():
        user_data = await state.get_data()
        user_action = user_data['action']
        with Session() as session:
            user_1 = session.query(User).filter_by(tg_id=user_id).first()
            user_weight = user_1.weight
            user_height = user_1.height
        list_data = [float(user_action), float(walking_duration), float(user_weight), float(user_height)]
        walk_1 = calc.read_package(workout_type='WLK', data=list_data)
        info = walk_1.show_training_info()
        msg = info.get_message()
        walk_distance = info.distance
        walk_speed = info.speed
        spent_calories = info.calories
        with Session() as session:
            user_1 = session.query(User).filter_by(tg_id=user_id).first()
            new_training = Walking(action=user_action, duration=walking_duration, user=user_1,
                                   distance=walk_distance, speed=walk_speed, spent_calories=spent_calories)
            session.add(new_training)
            session.commit()

        await message.answer(text=msg, parse_mode='HTML')
        await message.answer(text=txt.menu_text, reply_markup=get_menu())
    else:
        await message.answer(text=txt.incorrect_duration)
        await state.set_state(WalkingState.duration)


@router.message(SwimmingState.actions)
async def actions_handler_swimming(message: Message, state: FSMContext):
    """
    Функция сохраняет количество гребков
    :param message:
    :param state:
    :return: SwimmingState.duration
    """
    steps_swimming = message.text
    if steps_swimming.isdigit():
        await state.update_data(action=steps_swimming)
        await message.answer(text=txt.duration_running)
        await state.set_state(SwimmingState.duration)
    else:
        await message.answer(text=txt.incorrect_actions)
        await state.set_state(SwimmingState.actions)


@router.message(SwimmingState.duration)
async def swimming_handler_duration(message: Message, state: FSMContext):
    """
    Функция сохраняет длительность плавания
    :param message:
    :param state:
    :return: SwimmingState.length_pool
    """
    swimming_duration = message.text
    user_id = message.from_user.id
    if swimming_duration.isdigit():
        await state.update_data(duration=swimming_duration)
        await message.answer(text=txt.length_pool)
        await state.set_state(SwimmingState.length_pool)
    else:
        await message.answer(text=txt.incorrect_duration)
        await state.set_state(SwimmingState.duration)


@router.message(SwimmingState.length_pool)
async def insert_length_pool(message: Message, state: FSMContext):
    """
    Функция сохраняет длину бассейна
    :param message:
    :param state:
    :return: SwimmingState.count_pool
    """
    length_pool = message.text
    if length_pool.isdigit():
        await state.update_data(length_pool=length_pool)
        await message.answer(text=txt.count_pool)
        await state.set_state(SwimmingState.count_pool)
    else:
        await message.asnwer(text=txt.incorrect_length_pool)
        await state.set_state(SwimmingState.length_pool)


@router.message(SwimmingState.count_pool)
async def insert_count_pool(message: Message, state: FSMContext):
    """
    Функция запрашивает всю необходимую информацию в БД и производит расчёт потраченных калорий
    за тренировку по плаванию
    :param message:
    :param state:
    :return: сообщение о тренировке и потраченных калориях и возвращает меню с новой тренировкой или историей тренировок
    """
    count_pool = message.text
    user_id = message.from_user.id
    if count_pool.isdigit():
        user_data = await state.get_data()
        print(user_data)
        user_action = user_data['action']
        user_duration = user_data['duration']
        pool_length = user_data['length_pool']
        with Session() as session:
            user_1 = session.query(User).filter_by(tg_id=user_id).first()
            user_weight = user_1.weight
        list_data = [float(user_action), float(user_duration), float(user_weight),
                     float(pool_length), float(count_pool)]
        swim_1 = calc.read_package(workout_type='SWM', data=list_data)
        info = swim_1.show_training_info()
        msg = info.get_message()
        swim_distance = info.distance
        swim_speed = info.speed
        spent_calories = info.calories
        with Session() as session:
            user_1 = session.query(User).filter_by(tg_id=user_id).first()
            new_swimming = Swimming(action=user_action, duration=user_duration, user=user_1,
                                    length_pool=pool_length, count_pool=count_pool,
                                    distance=swim_distance,
                                    spent_calories=spent_calories, speed=swim_speed)
            # new_swimming.user.append(user_1)
            session.add(new_swimming)
            session.commit()
        await message.answer(text=msg, parse_mode='HTML')
        await message.answer(text=txt.menu_text, reply_markup=get_menu())
    else:
        await message.answer(text=txt.incorrect_count_pool)
        await state.set_state(SwimmingState.count_pool)



