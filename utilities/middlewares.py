# Python модули
from aiogram import BaseMiddleware
from aiogram.types import *
from typing import *

import datetime


# Локальные модули
from create_bot import db
from data_base.operations import user_add


# Классы
class StandardMiddleware(BaseMiddleware):
	async def __call__(
			self,
			handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
			event: Message | CallbackQuery,
			data: Dict[str, Any]
	) -> Any:
		user = event.from_user
		data['user'] = user
		await user_add(db=db, user=user)
		return await handler(event, data)
