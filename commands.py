from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_commands(bot: Bot):
    commands=[
        BotCommand(
            command = "start",
            description = "Начало работы"
        ),
        BotCommand(
            command = "search",
            description = "Найти книгу"
        ),BotCommand(
            command= "genre",
            description="Найти книгу по жанру"
        ),
        BotCommand(
            command = "list",
            description = "Список книг"
        ),
        BotCommand(
            command="new",
            description="Добавить книгу"
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())