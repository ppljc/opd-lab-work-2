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
from data_base.operations import doctors_get


# Переменные
router = Router(name='client')


# Классы
class FSMAppointment(StatesGroup):
	full_name = State()
	full_name_confirm = State()
	doctor = State()
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

		builder = InlineKeyboardBuilder()
		builder.button(text='Да ✅', callback_data='appointment_full_name|1')
		builder.button(text='Нет ❌', callback_data='appointment_full_name|0')
		builder.button(text='Назад ⬅️', callback_data='add_appointment')
		builder.adjust(2, 1)

		await first_message.edit_text(
			text=(
				f'<b>{message.text}</b>\n\n'
				f'🤔 Это верно?'
			),
			reply_markup=builder.as_markup()
		)

		await state.set_state(FSMAppointment.full_name_confirm)
		await state.update_data(full_name=message.text)

		logger.info(f'USER={message.from_user.id}, MESSAGE="full_name={message.text}"')
	except Exception as e:
		logger.error(f'USER={message.from_user.id}, MESSAGE="{e}"')


@router.callback_query(F.data.startswith('appointment_full_name'))
async def callback_appointment_full_name_confirm(query: CallbackQuery, state: FSMContext):
	try:
		await query.answer()
		data = query.data.split('|')
		confirm = int(data[1])

		if confirm:
			reply_markup = await doctors_get(db=db)

			await query.message.edit_text(
				text='👨‍⚕️ Выберите врача, к которому хотите попасть на приём:',
				reply_markup=reply_markup
			)

			await state.set_state(FSMAppointment.date)
		else:


		logger.info(f'USER={query.from_user.id}, MESSAGE="confirm={}"')
	except Exception as e:
		logger.error(f'USER={query.from_user.id}, MESSAGE="{e}"')
