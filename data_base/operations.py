# Python модули
from aiogram.utils.keyboard import InlineKeyboardBuilder

import datetime
import json


# Локальные модули
from data_base.sqlite_db import SQLiteDB


# Функции
async def user_add(db: SQLiteDB, user):
	date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	await db.insert(
		table='users',
		what={
			'date': date,
			'user_id': user.id,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'username': user.username,
			'appointments': json.dumps([])
		}
	)


async def doctors_get(db: SQLiteDB):
	doctors = await db.select(
		table='doctors',
	)

	builder = InlineKeyboardBuilder()

	for doctor in doctors:
		builder.button(text=doctor[2], callback_data=f'appointment_doctor|{doctor[0]}')

	builder.button(text='Назад ⬅️', callback_data='menu_main')
	builder.adjust(3, repeat=True)

	return builder.as_markup()
