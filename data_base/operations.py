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


async def doctor_areas_get(db: SQLiteDB):
	doctor_areas = await db.select(
		table='doctor_areas'
	)

	builder = InlineKeyboardBuilder()

	for doctor in doctor_areas:
		builder.button(text=doctor[2], callback_data=f'appointment_doctor_area|{doctor[0]}')

	builder.button(text='Назад ⬅️', callback_data='add_appointment')
	builder.adjust(3, repeat=True)

	return builder.as_markup()


async def doctors_get(db: SQLiteDB, doctor_area):
	doctors = await db.select(
		table='doctors',
		where={'doctor_area': doctor_area}
	)

	builder = InlineKeyboardBuilder()

	for doctor in doctors:
		builder.button(text=doctor[1], callback_data=f'appointment_doctor_username|{doctor[0]}')

	builder.button(text='Назад ⬅️', callback_data='appointment_full_name')
	builder.adjust(1, repeat=True)

	return builder.as_markup()


async def dates_get(db: SQLiteDB, doctor_area, doctor_username):
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
		work_end = datetime.time(17, 0)

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

	result = []
	for date in sorted(available_slots.keys()):
		result.append({
			"date": date.isoformat(),
			"available_times": sorted(available_slots[date])
		})

	return result
