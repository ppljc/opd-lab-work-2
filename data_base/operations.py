# Python модули
import asyncio

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
			'username': user.username
		}
	)


async def doctor_area_name_get(db: SQLiteDB, doctor_area):
	doctor_area_name = await db.select(
		table='doctor_areas',
		what=('doctor_area_name',),
		where={'doctor_area': doctor_area}
	)

	return doctor_area_name[0][0]


async def doctor_areas_get(db: SQLiteDB):
	doctor_areas = await db.select(
		table='doctor_areas'
	)

	builder = InlineKeyboardBuilder()

	for doctor in doctor_areas:
		builder.button(text=doctor[1], callback_data=f'appointment_doctor_area|{doctor[0]}')

	builder.button(text='Назад ⬅️', callback_data='add_appointment')
	builder.adjust(3, repeat=True)

	return builder.as_markup()


async def doctors_get(db: SQLiteDB, doctor_area):
	doctors = await db.select(
		table='doctors',
		where={'doctor_area': doctor_area}
	)

	doctor_area_name = await doctor_area_name_get(db=db, doctor_area=doctor_area)

	builder = InlineKeyboardBuilder()

	for doctor in doctors:
		builder.button(text=doctor[1], callback_data=f'appointment_doctor_username|{doctor[0]}')

	builder.button(text='Назад ⬅️', callback_data='appointment_full_name')
	builder.adjust(1, repeat=True)

	return builder.as_markup(), doctor_area_name


async def dates_get(db: SQLiteDB, doctor_area, doctor_username):
	doctor_full_name = await db.select(
		table='doctors',
		what=('doctor_full_name',),
		where={'doctor_username': doctor_username}
	)

	existing_appointments = await db.select(
		table='appointments',
		where={'doctor_area': doctor_area, 'doctor_username': doctor_username}
	)

	occupied_slots = set()
	for appt in existing_appointments:
		occupied_slots.add((appt[1], appt[2]))

	current_datetime = datetime.datetime.now()
	current_date = current_datetime.date()
	available_slots = {}

	for day_offset in range(7):
		target_date = current_date + datetime.timedelta(days=day_offset)

		work_start = datetime.time(9, 0)
		work_end = datetime.time(16, 30)

		if target_date == current_date:
			current_time = current_datetime.time()
			if current_time >= work_end:
				continue

			current_minute = current_time.minute
			remainder = current_minute % 30
			minutes_to_add = 30 - remainder if remainder != 0 else 0
			next_slot_time = (datetime.datetime.combine(datetime.date.today(), current_time) +
			                  datetime.timedelta(minutes=minutes_to_add)).time()

			if next_slot_time >= work_end:
				continue
			start_time = next_slot_time
		else:
			start_time = work_start

		start_datetime = datetime.datetime.combine(target_date, start_time)
		end_datetime = datetime.datetime.combine(target_date, work_end)

		slot = start_datetime
		while slot <= end_datetime:
			slot_date_str = slot.date().isoformat()
			slot_time_str = slot.time().strftime("%H:%M")

			if (slot_date_str, slot_time_str) not in occupied_slots:
				if target_date not in available_slots:
					available_slots[target_date] = []
				available_slots[target_date].append(slot_time_str)

			slot += datetime.timedelta(minutes=30)

	builder = InlineKeyboardBuilder()
	builders_date = {}

	for date in sorted(available_slots.keys()):
		builder.button(text=f'{date.strftime("%d.%m.%Y")} ({len(available_slots[date])})', callback_data=f'appointment_date|{date.strftime("%d.%m.%Y")}')

		builder_date = InlineKeyboardBuilder()
		for time in sorted(available_slots[date]):
			builder_date.button(text=f'{time}', callback_data=f'appointment_time|{date.strftime("%d.%m.%Y")}|{time}')

		builder_date.button(text='Назад ⬅️', callback_data=f'appointment_doctor_username|{doctor_username}')
		builder_date.adjust(3, repeat=True)

		builders_date[date.strftime("%d.%m.%Y")] = builder_date.as_markup()

	builder.button(text='Назад ⬅️', callback_data=f'appointment_doctor_area|{doctor_area}')
	builder.adjust(2, repeat=True)

	return builder.as_markup(), builders_date, doctor_full_name[0][0]


async def appointment_add(db: SQLiteDB, user_id, date, time, doctor_area, doctor_username):
	await db.insert(
		table='appointments',
		what={
			'user_id': user_id,
			'date': date,
			'time': time,
			'doctor_area': doctor_area,
			'doctor_username': doctor_username
		}
	)


async def appointments_get(db: SQLiteDB, user_id):
	appointments = await db.select(
		table='appointments',
		where={'user_id': user_id}
	)

	text = '📄 Вот список ваших записей:'
	builder = InlineKeyboardBuilder()

	for appointment in appointments:
		doctor_area_name = await doctor_area_name_get(db=db, doctor_area=appointment[3])

		builder.button(text=f'{appointment[1]} {appointment[2]} {doctor_area_name}', callback_data=f'edit_appointment|{appointment[1]}|{appointment[2]}|{appointment[3]}|{appointment[4]}')

	if not appointments:
		text = '📎 У вас пока нет записей.'

	builder.button(text='Назад ⬅️', callback_data='menu_main')
	builder.adjust(1, repeat=True)

	return text, builder.as_markup()


async def appointment_get(db: SQLiteDB, date, time, doctor_area, doctor_username):
	doctor_area_name = await doctor_area_name_get(db=db, doctor_area=doctor_area)

	doctor_full_name = await db.select(
		table='doctors',
		what=('doctor_full_name',),
		where={'doctor_username': doctor_username}
	)

	text = (
		f'Ваша запись на {date} {time}:\n\n'
		f'Направление: {doctor_area_name}\n'
		f'Доктор: {doctor_full_name[0][0]}'
	)

	builder = InlineKeyboardBuilder()
	builder.button(text='Отменить ❌', callback_data=f'remove_appointment|{date}|{time}|{doctor_area}|{doctor_username}')
	builder.button(text='Назад ⬅️', callback_data=f'list_appointments')
	builder.adjust(2)

	return text, builder.as_markup()


async def appointment_remove(db: SQLiteDB, user_id, date, time, doctor_area, doctor_username):
	await db.remove(
		table='appointments',
		where={'user_id': user_id, 'date': date, 'time': time, 'doctor_area': doctor_area, 'doctor_username': doctor_username}
	)
