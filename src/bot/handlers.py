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
# from bot.models import User, Base, Running, Walking, Swimming, association_table_running, association_table_walking, association_table_swimming
from bot.models import User, Base, Running, Swimming
from bot import calculations as calc


from datetime import datetime


router = Router()

engine = create_engine('postgresql://postgres:03121981@localhost:5432/dg_tg_bot')

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


@router.message(Command("start"))
async def start_handler(message: Message):
    # Проверка на регистрацию пользователя в бд
    user_id = message.from_user.id
    # проверить есть ли пользователь уже в базе и изменить логику, чтобы проверять айди а не имя
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
    await state.set_state(DataState.age)
    await call.message.answer(text=txt.age)


@router.message(DataState.age)
async def age_handler(message: Message, state: FSMContext):
    age = message.text
    # print(type(age))
    r = range(0, 120)
    if age.isdigit() and float(age) in r:
        await state.update_data(age=age)
        await state.set_state(DataState.height)
        await message.answer(text=txt.height)
    else:
        await state.set_state(DataState.age)
        await message.answer(text=txt.incorrect_age_letters)


@router.message(DataState.height)
async def age_handler(message: Message, state: FSMContext):
    height = message.text
    # print(type(age))
    r = range(50, 230)
    if height.isdigit() and float(height) in r:
        await state.update_data(height=height)
        await state.set_state(DataState.weight)
        await message.answer(text=txt.weight)
    else:
        await state.set_state(DataState.height)
        await message.answer(text=txt.incorrect_height)


@router.message(DataState.weight)
async def age_handler(message: Message, state: FSMContext):
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

    # all_data = await state.update_data(data={'weight': weight}) # take all data from height handler , check all data if it is correct
    # print(all_data)
# Handler, который сработает на выбор тренировки
# handler, который сработает на определенную тренировку

# дописать роутер для сохранения роста
@router.callback_query(F.data == "info")
async def sport_handler(call: types.CallbackQuery):
    await call.message.edit_text(text=txt.choice_text, reply_markup=choice_sport())


@router.callback_query(F.data == "history")
async def sport_handler(call: types.CallbackQuery):
    user_id = call.from_user.id
    print(user_id)
    with Session() as session:
        user_1 = session.query(User).filter_by(tg_id=user_id).first()
        id_1 = user_1.user_id
        trainings_runnig = session.query(association_table_running).filter_by(user_id=id_1).all() # получаем котеж , который включает id тренировок
        trainings_walking = session.query(association_table_walking).filter_by(user_id=id_1).all()
        trainings_swimming = session.query(association_table_swimming).filter_by(user_id=id_1).all()
        print(trainings_runnig, trainings_walking, trainings_swimming)
        for info_run in trainings_runnig: # получаем id тренировки из кортежа
            print(info_run)
            run_id = info_run[2]
            print(run_id)
            training_run = session.query(Running).filter_by(id=run_id).first() # получаем экземпляр класса Running
            print(training_run)
            # await call.message.answer(text=training_run)
        for info_walk in trainings_walking: # получаем id тренировки из кортежа
            print(info_walk)
            walk_id = info_walk[2]
            print(walk_id)
            training_walk = session.query(Walking).filter_by(id=run_id).first() # получаем экземпляр класса Walking
            print(training_walk)
        for info_swim in trainings_swimming: # получаем id тренировки из кортежа
            print(info_swim)
            swim_id = info_swim[2]
            print(swim_id)
            training_swim = session.query(Swimming).filter_by(id=run_id).first() # получаем экземпляр класса Swimming
            print(training_swim)

    await call.message.edit_text(text=txt.choice_text, reply_markup=choice_sport())


@router.callback_query(F.data.startswith("sport"))
async def sport_handler(call: types.CallbackQuery, state: FSMContext):
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
    steps_running = message.text
    if steps_running.isdigit():
        await state.update_data(action=steps_running)
        await message.answer(text=txt.duration_running)
        await state.set_state(RunState.duration)
    else:
        await message.answer(text=txt.incorrect_actions)
        await state.set_state(RunState.actions)


@router.message(RunState.duration)
async def actions_handler_duration(message: Message, state: FSMContext):
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
    # elif sport_type == "walking":
    #     walking_duration = message.text
    #     if walking_duration.isdigit():
    #         await state.update_data(duration=walking_duration)
    #         await message.answer(text=txt.height_walking)
    #         await state.set_state(WalkingState.height)
    # elif sport_type == "swimming":
    #     swimming_duration = message.text
    #     print(swimming_duration)
    #     if swimming_duration.isdigit():
    #         await state.update_data(duration=swimming_duration)
    #         await message.answer(text=txt.length_pool)
    #         await state.set_state(SwimmingState.length_pool)


# @router.message(WalkingState.height)
# async def insert_height(message: Message, state: FSMContext):
#     height = message.text
#     user_id = message.from_user.id
#     if height.isdigit():
#         user_data = await state.get_data()
#         user_action = user_data['action']
#         user_duration = user_data['duration']
#         training_date = datetime.now()
#         with Session() as session:
#             user_1 = session.query(User).filter_by(tg_id=user_id).first()
#             user_weight = user_1.weight
#         list_data = [float(user_action), float(user_duration), float(user_weight), float(height)]
#         walk_1 = calc.read_package(workout_type='WLK', data=list_data)
#         info = walk_1.show_training_info()
#         msg = info.get_message()
#         walk_distance = info.distance
#         walk_speed = info.speed
#         spent_calories = info.calories
#         with Session() as session:
#             user_1 = session.query(User).filter_by(tg_id=user_id).first()
#             new_walking = Walking(action=user_action, duration=user_duration, height=height,
#                                   date=training_date, distance=walk_distance, speed=walk_speed,
#                                   calories=spent_calories)
#             new_walking.user.append(user_1)
#             session.add(new_walking)
#             session.commit()
#         await message.answer(text=msg, parse_mode='HTML')
#         await message.answer(text=txt.menu_text, reply_markup=get_menu())
#     else:
#         await message.answer(text=txt.incorrect_height)
#         await state.set_state(WalkingState.height)


@router.message(SwimmingState.length_pool)
async def insert_length_pool(message: Message, state: FSMContext):
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
    count_pool = message.text
    user_id = message.from_user.id
    if count_pool.isdigit():
        user_data = await state.get_data()
        print(user_data)
        user_action = user_data['action']
        user_duration = user_data['duration']
        pool_length = user_data['length_pool']
        training_date = datetime.now()
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
            new_swimming = Swimming(action=user_action, duration=user_duration, length_pool=pool_length,
                                    count_pool=count_pool, date=training_date, distance=swim_distance,
                                    calories=spent_calories, speed=swim_speed)
            new_swimming.user.append(user_1)
            session.add(new_swimming)
            session.commit()
        await message.answer(text=msg, parse_mode='HTML')
        await message.answer(text=txt.menu_text, reply_markup=get_menu())
    else:
        await message.answer(text=txt.incorrect_count_pool)
        await state.set_state(SwimmingState.count_pool)




    # установить новое состояние в этом же роутере (для веса, например) и дописать код для записи данных в базу
    #
    #
    # session.close()
    # Сохранить в бд значение action этого пользователя
    # Через await отправить требование ввести времени тренировки (duration)
    # Включить другое состояние await state.set_state(RunState.actions)
    # И после написать новый хендрел для этого состояния

# router = Router()

# # Handler, который сработает на выбор тренировки
# # handler, который сработает на определенную тренировку

#
#
#     # Нужно с помощью split достать, ту тренировку которую выбрал человек
