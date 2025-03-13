# Python модули
import aiosqlite


# Локальные модули
from utilities.logger import logger


# Классы
class SQLiteDB:
	def __init__(self, db_name):
		self.db_name = db_name
		self.connection = None

	async def connect(self):
		try:
			self.connection = await aiosqlite.connect(self.db_name)
			await self.connection.execute(
				'''
					CREATE TABLE IF NOT EXISTS users 
					(date DATE, user_id INTEGER UNIQUE, first_name TEXT, last_name TEXT, 
					username TEXT UNIQUE)
				'''
			)
			await self.connection.execute(
				'''
					CREATE TABLE IF NOT EXISTS appointments 
					(user_id INTEGER, date DATE, time TEXT, doctor_area TEXT, doctor_username TEXT)
				'''
			)
			await self.connection.execute(
				'''
					CREATE TABLE IF NOT EXISTS doctor_areas 
					(doctor_area TEXT, doctor_area_name TEXT)
				'''
			)
			await self.connection.execute(
				'''
					CREATE TABLE IF NOT EXISTS doctors 
					(doctor_username TEXT UNIQUE, doctor_full_name TEXT, doctor_area TEXT)
				'''
			)
			await self.connection.commit()
			return True
		except Exception as e:
			logger.error(f'USER=BOT, MESSAGE="{e}"')
			return False

	async def close(self):
		try:
			await self.connection.close()
			return True
		except Exception as e:
			logger.error(f'USER=BOT, MESSAGE="{e}"')
			return False

	async def insert(self, table: str, what: dict) -> bool:
		try:
			columns = ','.join(what.keys())
			placeholders = ','.join(['?'] * len(what))
			values = tuple(what.values())

			query = f'''INSERT INTO {table} ({columns}) VALUES ({placeholders})'''
			await self.connection.execute(query, values)
			await self.connection.commit()

			logger.debug(f'USER=BOT, MESSAGE="table={table}, what={what}"')
			return True
		except aiosqlite.IntegrityError:
			logger.debug(f'USER=BOT, MESSAGE="UNIQUE ALREADY EXISTS | table={table}, what={what}"')
			return False
		except Exception as e:
			logger.error(f'USER=BOT, MESSAGE="{e}"')
			return False

	async def select(self, table: str, what: tuple | None = None, where: dict | None = None):
		try:
			what_clause = '*' if not what else ', '.join(what)

			if where:
				where_clause = ' AND '.join([f'{key} = ?' for key in where.keys()])
				where_values = tuple(where.values())
				query = f'''SELECT {what_clause} FROM {table} WHERE {where_clause}'''
				cursor = await self.connection.execute(query, where_values)
			else:
				query = f'''SELECT {what_clause} FROM {table}'''
				cursor = await self.connection.execute(query)

			rows = await cursor.fetchall()
			logger.debug(
				f'USER=BOT, MESSAGE="table={table}, what={what_clause}, where={where}, '
				f'result_len={len(rows)}"'
			)
			return rows
		except Exception as e:
			logger.error(f'USER=BOT, MESSAGE="{e}"')
			return []

	async def update(self, table: str, what: dict, where: dict | None = None):
		try:
			what_clause = ', '.join([f'{col} = ?' for col in what.keys()])
			what_values = tuple(what.values())

			if where:
				where_clause = ' AND '.join([f'{col} = ?' for col in where.keys()])
				where_values = tuple(where.values())
				query = f'''UPDATE {table} SET {what_clause} WHERE {where_clause}'''
				values = what_values + where_values
			else:
				query = f'''UPDATE {table} SET {what_clause}'''
				values = what_values

			cursor = await self.connection.execute(query, values)
			await self.connection.commit()

			affected_rows = cursor.rowcount
			logger.debug(
				f'USER=BOT, MESSAGE="table={table}, what={what}, where={where}, '
				f'affected_rows={affected_rows}"'
			)
			return affected_rows
		except Exception as e:
			logger.error(f'USER=BOT, MESSAGE="{e}"')
			return 0

	async def remove(self, table: str, where: dict | None = None) -> int:
		try:
			if where:
				where_clause = ' AND '.join([f'{key} = ?' for key in where.keys()])
				where_values = tuple(where.values())
				query = f'''DELETE FROM {table} WHERE {where_clause}'''
				cursor = await self.connection.execute(query, where_values)
			else:
				query = f'''DELETE FROM {table}'''
				cursor = await self.connection.execute(query)

			await self.connection.commit()
			affected_rows = cursor.rowcount
			logger.debug(
				f'USER=BOT, MESSAGE="table={table}, where={where}, affected_rows={affected_rows}"'
			)
			return affected_rows
		except Exception as e:
			logger.error(f'USER=BOT, MESSAGE="{e}"')
			return 0

