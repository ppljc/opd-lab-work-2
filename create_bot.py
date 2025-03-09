# Python модули
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage


# Локальные модули
import config

from data_base.sqlite_db import SQLiteDB


# Основные объекты для взаимодействия
def_props = DefaultBotProperties(
	parse_mode='HTML',
	link_preview_is_disabled=True
)

bot = Bot(
	token=config.BOT_TOKEN,
	default=def_props
)

dp = Dispatcher(
	storage=MemoryStorage()
)

db = SQLiteDB(
	db_name='base.db'
)
