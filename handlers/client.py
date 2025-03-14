# Python модули
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import *
from aiogram.filters import Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup


# Локальные модули
from create_bot import db
from utilities.logger import logger
from data_base.operations import (
	doctors_get, doctor_areas_get, dates_get, appointment_add, appointments_get, appointment_get,
	doctor_area_name_get, appointment_remove
)


# Переменные
router = Router(name='client')


# Классы
class FSMAppointment(StatesGroup):
	full_name = State()
	doctor_area = State()
	doctor_area_name = State()
	doctor_username = State()
	doctor_full_name = State()
	builders_date = State()
	date = State()
	time = State()
	first_message = State()


# Функции
@router.message(Command(commands=['start'], ignore_case=True))
async def message_start(message: Message, state: FSMContext):
	try:
		await state.clear()

		await message.delete()

		builder = InlineKeyboardBuilder()
		builder.button(text='Записаться 🆕', callback_data='add_appointment')
		builder.button(text='Мои записи 📄', callback_data='list_appointments')
		builder.adjust(2)

		await message.answer(
			text=(
				'👋 Привет! Вас приветствует бот-помощник Омской Областной Региональной Федеральной Межконтинентальной Больницы.\n\n'
				'🏥 Я с радостью помогу вам записаться на приём, жмите кнопку ниже!'
			),
			reply_markup=builder.as_markup()
		)

		logger.info(f'USER={message.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={message.from_user.id}, MESSAGE="{e}"')


@router.callback_query(F.data == 'menu_main')
async def callback_menu_main(query: CallbackQuery, state: FSMContext):
	try:
		await state.clear()

		await query.answer()

		builder = InlineKeyboardBuilder()
		builder.button(text='Записаться 🆕', callback_data='add_appointment')
		builder.button(text='Мои записи 📄', callback_data='list_appointments')
		builder.adjust(2)

		await query.message.edit_text(
			text=(
				'👋 Привет! Вас приветствует бот-помощник Омской Областной Региональной Федеральной Межконтинентальной Больницы.\n\n'
				'🏥 Я с радостью помогу вам записаться на приём, жмите кнопку ниже!'
			),
			reply_markup=builder.as_markup()
		)

		logger.info(f'USER={query.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


@router.callback_query(F.data == 'add_appointment')
async def callback_appointment_add(query: CallbackQuery, state: FSMContext):
	try:
		await state.clear()

		await query.answer()

		builder = InlineKeyboardBuilder()
		builder.button(text='Назад ⬅️', callback_data='menu_main')

		await query.message.edit_text(
			text='💁‍♂️ Отправьте своё ФИО:',
			reply_markup=builder.as_markup()
		)

		await state.set_state(FSMAppointment.full_name)
		await state.update_data(first_message=query.message)

		logger.info(f'USER={query.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


@router.message(StateFilter(FSMAppointment.full_name))
async def message_appointment_full_name(message: Message, state: FSMContext):
	try:
		data = await state.get_data()
		first_message = data['first_message']

		await message.delete()

		reply_markup = await doctor_areas_get(db=db)

		await first_message.edit_text(
			text=f'👨‍⚕️ {message.text}, выберите направление, на которое хотите попасть на приём:',
			reply_markup=reply_markup
		)

		await state.set_state(FSMAppointment.doctor_area)
		await state.update_data(full_name=message.text)

		logger.info(f'USER={message.from_user.id}, MESSAGE="full_name={message.text}"')
	except Exception as e:
		logger.error(f'USER={message.from_user.id}, MESSAGE="{e}"')


@router.callback_query(F.data == 'appointment_full_name')
async def callback_appointment_full_name(query: CallbackQuery, state: FSMContext):
	try:
		data = await state.get_data()
		first_message = data['first_message']
		full_name = data['full_name']

		await query.answer()

		reply_markup = await doctor_areas_get(db=db)

		await first_message.edit_text(
			text=f'👨‍⚕️ {full_name}, выберите направление, на которое хотите попасть на приём:',
			reply_markup=reply_markup
		)

		await state.set_state(FSMAppointment.doctor_area)

		logger.info(f'USER={query.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


@router.callback_query(F.data.startswith('appointment_doctor_area'))
async def callback_appointment_doctor_area(query: CallbackQuery, state: FSMContext):
	try:
		data = await state.get_data()
		full_name = data['full_name']

		await query.answer()
		doctor_area = query.data.split('|')[1]

		reply_markup, doctor_area_name = await doctors_get(db=db, doctor_area=doctor_area)

		await query.message.edit_text(
			text=f'👨‍⚕️ {full_name}, выберите врача по направлению «{doctor_area_name}», к которому хотите попасть на приём:',
			reply_markup=reply_markup
		)

		await state.set_state(FSMAppointment.doctor_username)
		await state.update_data(
			doctor_area=doctor_area,
			doctor_area_name=doctor_area_name
		)

		logger.info(f'USER={query.from_user.id}, MESSAGE="doctor_area={doctor_area}"')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


@router.callback_query(F.data.startswith('appointment_doctor_username'))
async def callback_appointment_doctor_username(query: CallbackQuery, state: FSMContext):
	try:
		data = await state.get_data()
		full_name = data['full_name']
		doctor_area = data['doctor_area']
		doctor_area_name = data['doctor_area_name']

		await query.answer()
		doctor_username = query.data.split('|')[1]

		reply_markup, builders_date, doctor_full_name = await dates_get(db=db, doctor_area=doctor_area, doctor_username=doctor_username)

		await query.message.edit_text(
			text=f'🗓️ {full_name}, на какую дату вы хотите записаться к врачу «{doctor_full_name}» по направлению «{doctor_area_name}»:',
			reply_markup=reply_markup
		)

		await state.set_state(FSMAppointment.date)
		await state.update_data(
			doctor_username=doctor_username,
			doctor_full_name=doctor_full_name,
			builders_date=builders_date
		)

		logger.info(f'USER={query.from_user.id}, MESSAGE="doctor_username={doctor_username}"')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


@router.callback_query(F.data.startswith('appointment_date'))
async def callback_appointment_date(query: CallbackQuery, state: FSMContext):
	try:
		data = await state.get_data()
		full_name = data['full_name']
		doctor_full_name = data['doctor_full_name']
		doctor_area_name = data['doctor_area_name']
		builders_date = data['builders_date']

		await query.answer()
		date = query.data.split('|')[1]

		await query.message.edit_text(
			text=f'⌚ {full_name}, на какое время вы хотите записаться к врачу «{doctor_full_name}» по направлению «{doctor_area_name}» на {date}:',
			reply_markup=builders_date[date]
		)

		await state.set_state(FSMAppointment.time)
		await state.update_data(date=date)

		logger.info(f'USER={query.from_user.id}, MESSAGE="date={query.data}"')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


@router.callback_query(F.data.startswith('appointment_time'))
async def callback_appointment_time(query: CallbackQuery, state: FSMContext):
	try:
		data = await state.get_data()
		full_name = data['full_name']
		doctor_area = data['doctor_area']
		doctor_area_name = data['doctor_area_name']
		doctor_username = data['doctor_username']
		doctor_full_name = data['doctor_full_name']

		await query.answer()
		date = query.data.split('|')[1]
		time = query.data.split('|')[2]

		await appointment_add(
			db=db,
			user_id=query.from_user.id,
			date=date,
			time=time,
			doctor_area=doctor_area,
			doctor_username=doctor_username
		)

		builder = InlineKeyboardBuilder()
		builder.button(text='Назад ⬅️', callback_data='menu_main')

		await query.message.edit_text(
			text=f'✅ {full_name}, вы успешно записаны к «{doctor_full_name}» на направление «{doctor_area_name}» на {date} в {time}!',
			reply_markup=builder.as_markup()
		)

		await state.clear()

		logger.info(f'USER={query.from_user.id}, MESSAGE="time={time}"')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


@router.callback_query(F.data == 'list_appointments')
async def callback_appointment_list(query: CallbackQuery):
	try:
		await query.answer()

		text, reply_markup = await appointments_get(db=db, user_id=query.from_user.id)

		await query.message.edit_text(
			text=text,
			reply_markup=reply_markup
		)

		logger.info(f'USER={query.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


@router.callback_query(F.data.startswith('edit_appointment'))
async def callback_appointment_edit(query: CallbackQuery):
	try:
		await query.answer()
		date = query.data.split('|')[1]
		time = query.data.split('|')[2]
		doctor_area = query.data.split('|')[3]
		doctor_username = query.data.split('|')[4]

		text, reply_markup = await appointment_get(db=db, date=date, time=time, doctor_area=doctor_area, doctor_username=doctor_username)

		await query.message.edit_text(
			text=text,
			reply_markup=reply_markup
		)

		logger.info(f'USER={query.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


@router.callback_query(F.data.startswith('remove_appointment'))
async def callback_appointment_remove(query: CallbackQuery):
	try:
		await query.answer()
		date = query.data.split('|')[1]
		time = query.data.split('|')[2]
		doctor_area = query.data.split('|')[3]
		doctor_username = query.data.split('|')[4]

		doctor_area_name = await doctor_area_name_get(db=db, doctor_area=doctor_area)

		builder = InlineKeyboardBuilder()
		builder.button(text='Да 🗑️', callback_data=f'confirm_remove_appointment|{date}|{time}|{doctor_area}|{doctor_username}')
		builder.button(text='Назад ⬅️', callback_data=f'edit_appointment|{date}|{time}|{doctor_area}|{doctor_username}')
		builder.adjust(2)

		await query.message.edit_text(
			text=f'❔ Вы уверены, что хотите удалить запись на {date} в {time} к {doctor_area_name}?',
			reply_markup=builder.as_markup()
		)

		logger.info(f'USER={query.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')


@router.callback_query(F.data.startswith('confirm_remove_appointment'))
async def callback_appointment_confirm_remove(query: CallbackQuery):
	try:
		await query.answer()
		date = query.data.split('|')[1]
		time = query.data.split('|')[2]
		doctor_area = query.data.split('|')[3]
		doctor_username = query.data.split('|')[4]

		await appointment_remove(db=db, user_id=query.from_user.id, date=date, time=time, doctor_area=doctor_area, doctor_username=doctor_username)

		await callback_appointment_list(query=query)

		logger.info(f'USER={query.from_user.id}, MESSAGE=""')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')
