# Python модули
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


# Локальные модули
from utilities.logger import logger
from utilities.values import read_values


# Классы
class IsAdmin(BaseFilter):
    async def __call__(self, data: Message | CallbackQuery) -> bool:
        try:
            admins = await read_values('admins')
            return data.from_user.id in admins
        except Exception as e:
            logger.error(f'USER={data.from_user.id}, MESSAGE="IsAdmin={e}"')
            return False
