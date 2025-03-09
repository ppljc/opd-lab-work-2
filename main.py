# Python модули
from aiogram.types.bot_command import BotCommand

import asyncio
import nest_asyncio
import platform


# Локальные модули
from create_bot import bot, dp, db
from handlers import client
from utilities.logger import logger
from utilities.values import read_values
from utilities.middlewares import StandardMiddleware


# Функции при запуске и выключении бота
async def on_startup():
	nest_asyncio.apply()

	await bot.set_my_commands(commands=[
		BotCommand(command='/start', description='Запустить/Перезапустить бота'),
	])

	bot_user = await bot.get_me()

	if await db.connect():
		logger.info(f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="database started"')
	else:
		logger.error(f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="database NOT started"')

	logger.info(f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="up and running..."')

	await read_values(file='admins')


async def on_shutdown():
	bot_user = await bot.get_me()

	if await db.close():
		logger.info(f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="database finished"')
	else:
		logger.error(f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="database NOT finished correct"')

	logger.info(f'BOT_NAME="{bot_user.full_name}", BOT_USERNAME="{bot_user.username}", MESSAGE="shutting down..."')


# Функция запуска бота
async def main():
	dp.startup.register(on_startup)
	dp.shutdown.register(on_shutdown)

	dp.include_routers(
		client.router
	)

	dp.message.middleware(StandardMiddleware())
	dp.callback_query.middleware(StandardMiddleware())

	await bot.delete_webhook(drop_pending_updates=True)
	await dp.start_polling(bot)


# Запуск бота
if __name__ == '__main__':
	try:
		if platform.system() == 'Windows':
			asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

		asyncio.run(main())
	except KeyboardInterrupt:
		asyncio.run(bot.session.close())
