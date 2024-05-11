import config
from aiogram import types, Bot, Dispatcher
import asyncio
import logging
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.command import Command
import database as db
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from collections import Counter
from commands import set_commands

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher()


class add_Book(StatesGroup):
    nw_title = State()
    nw_author = State()
    nw_description = State()
    nw_genre = State()


class search_Book(StatesGroup):
    search_book = State()


class List(StatesGroup):
    list_id = State()
    added_book = State()


class Search_by_Genre(StatesGroup):
    search_book_by_genre = State()


@dp.startup()
async def start_bot(bot: Bot):
    await set_commands(bot)  # Установка команд бота при его запуске


@dp.message(Command(commands=["start"]))
async def command_start(message: types.Message):
    # Инициализация данных пользователя в базе данных
    await db.db_start(message.from_user.id)
    # Отправка приветственного сообщения пользователю
    await bot.send_message(message.from_user.id, f"Привет {message.chat.first_name}")


@dp.message(Command(commands=["new"]))
async def new_book_title(message: types.Message, state: FSMContext):
    # Установка состояния для ввода названия новой книги
    await state.set_state(add_Book.nw_title)
    # Запрос названия книги у пользователя
    await bot.send_message(message.chat.id, "Введите название книги:")


@dp.message(add_Book.nw_title)
async def new_book_title(message: types.Message, state: FSMContext):
    # Сохранение введенного названия книги в состояние
    await state.update_data(nw_title=message.text.lower())
    # Переход к следующему состоянию для ввода автора книги
    await state.set_state(add_Book.nw_author)
    # Запрос автора книги у пользователя
    await bot.send_message(message.chat.id, "Введите автора книги:")


@dp.message(add_Book.nw_author)
async def new_book_author(message: types.Message, state: FSMContext):
    # Сохранение введенного автора книги в состояние
    await state.update_data(nw_author=message.text.lower())
    # Переход к следующему состоянию для ввода описания книги
    await state.set_state(add_Book.nw_description)
    # Запрос описания книги у пользователя
    await bot.send_message(message.chat.id, "Введите описание книги:")


@dp.message(add_Book.nw_description)
async def new_book_description(message: types.Message, state: FSMContext):
    # Сохранение введенного описания книги в состояние
    await state.update_data(nw_description=message.text.lower())
    # Переход к следующему состоянию для выбора жанра книги
    await state.set_state(add_Book.nw_genre)
    # Получение списка всех жанров из базы данных
    genres_list = await db.get_all_genres(message.chat.id)
    buttons = [
        InlineKeyboardButton(
            text=genre,
            callback_data=f'{genre}') for genre in genres_list]  # Создание кнопок для каждого жанра
    # Создание inline-клавиатуры с кнопками жанров
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons], row_width=1)
    if genres_list:
        # Запрос жанра книги с клавиатурой
        await bot.send_message(message.chat.id, "Введите жанр книги: (можно другой)", reply_markup=keyboard)
    else:
        # Запрос жанра книги без клавиатуры
        await bot.send_message(message.chat.id, "Введите жанр книги:")


@dp.message(add_Book.nw_genre)
async def new_book_genre(message: types.Message, state: FSMContext):
    # Сохранение введенного жанра книги в состояние
    await state.update_data(nw_genre=message.text.lower())
    data = await state.get_data()  # Получение всех данных о новой книге
    # Добавление новой книги в базу данных
    await db.new_book(message.chat.id, data["nw_title"], data["nw_author"], data["nw_description"], data["nw_genre"])
    # Уведомление пользователя об успешном добавлении книги
    await bot.send_message(message.from_user.id, "Книга успешно добавлена")
    await state.clear()  # Очистка состояния


@dp.message(Command('genre'))
async def in_genre(message: types.Message, state: FSMContext):
    # Установка состояния для поиска книги по жанру
    await state.set_state(Search_by_Genre.search_book_by_genre)
    # Запрос жанра для поиска
    await bot.send_message(message.chat.id, "Введите жанр:")


@dp.message(Search_by_Genre.search_book_by_genre)
async def search_book_by_genre(message: types.Message, state: FSMContext):
    # Сохранение введенного жанра для поиска в состояние
    await state.update_data(genre=message.text.lower())
    data = await state.get_data()  # Получение данных о жанре для поиска
    # Поиск книг по жанру в базе данных
    book = await db.search_by_genre(message.chat.id, data["genre"])
    if book:
        respones = ''.join(
            [
                f'"{title.capitalize()}", {author.title()}\nОписание: {description}\nЖанр: {genre}\n\n' for title,
                author,
                description,
                genre in book])  # Формирование ответа с найденными книгами
    else:
        respones = 'Книги по данному жанру не найдены.'  # Ответ, если книги не найдены
    # Отправка ответа пользователю
    await bot.send_message(message.chat.id, respones)
    await state.clear()  # Очистка состояния


@dp.message(Command('list'))
async def list(message: types.Message, state: FSMContext):
    # Получение списка всех книг пользователя
    books = await db.list_books(message.chat.id)
    if books:
        # Установка состояния для выбора книги из списка
        await state.set_state(List.list_id)
        # Получение всех идентификаторов книг
        all_id_books = await db.get_all_id_book(message.chat.id)
        # Определение количества кнопок в ряду на клавиатуре
        row_width = 2 if len(all_id_books) > 6 else 1
        buttons = [
            InlineKeyboardButton(
                text=str(id_book),
                callback_data=f'{id_book}') for id_book in all_id_books]  # Создание кнопок для каждой книги
        # Группировка кнопок по рядам
        keyboard_buttons = [buttons[i:i + row_width]
                            for i in range(0, len(buttons), row_width)]
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=keyboard_buttons,
            row_width=row_width)  # Создание клавиатуры с кнопками
        response = '\n'.join(
            [
                f'{id_book}) "{title.capitalize()}", {author.title()}' for id_book,
                title,
                author in books])  # Формирование списка книг
        # Отправка списка книг с клавиатурой
        await bot.send_message(message.chat.id, f'{response}\n\nПодробнее:', reply_markup=keyboard)
    else:
        # Сообщение, если книги отсутствуют
        await bot.send_message(message.chat.id, "Книги не найдены.")


@dp.callback_query(List.list_id)
async def calback_query_list(call: types.CallbackQuery, state: FSMContext):
    # Сохранение идентификатора выбранной книги
    await state.update_data(list_id=call.data)
    # Установка состояния для работы с выбранной книгой
    await state.set_state(List.added_book)
    data = await state.get_data()  # Получение данных о выбранной книге
    # Поиск книги по идентификатору
    book = await db.search_book_by_id(call.from_user.id, data["list_id"])
    respones = ''.join(
        [
            f'"{title.capitalize()}", {author.title()}\nОписание: {description}\nЖанр: {genre}' for title,
            author,
            description,
            genre in book])  # Формирование ответа с информацией о книге
    # Отправка информации о книге с клавиатурой для удаления
    await bot.send_message(call.from_user.id, respones, reply_markup=del_book)

del_book = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(
        text="Удалить книгу",
        callback_data="del_book"
    )
]
])  # Создание клавиатуры для удаления книги


@dp.callback_query(List.added_book)
async def callback_query_delete(
        call: types.CallbackQuery,
        state: FSMContext,
        bot: Bot):
    if call.data == "del_book":
        data = await state.get_data()  # Получение данных о книге для удаления
        # Удаление книги из базы данных
        await db.del_book(call.from_user.id, data["list_id"])
        # Сообщение об успешном удалении книги
        await bot.send_message(call.from_user.id, "Книга успешно удалена")
        await state.clear()  # Очистка состояния


@dp.message(Command('search'))
async def search_book(message: types.Message, state: FSMContext):
    # Установка состояния для поиска книги
    await state.set_state(search_Book.search_book)
    # Запрос ключевого слова для поиска
    await bot.send_message(message.chat.id, "Найти книгу по ключевому слову:")


@dp.message(search_Book.search_book)
async def search_command(message: types.Message, state: FSMContext, bot: Bot):
    word = message.text.lower()  # Сохранение ключевого слова для поиска
    # Поиск книг по ключевому слову
    books = await db.search_books_by_word(message.chat.id, word)
    if books:
        # Формирование списка найденных книг
        response = '\n'.join(
            [f'"{title.capitalize()}", {author.title()}' for title, author in books])
        # Отправка списка найденных книг
        await bot.send_message(message.chat.id, f'Результаты поиска:\n\n{response}')
    else:
        # Сообщение, если книги не найдены
        await bot.send_message(message.chat.id, "Книги с таким ключевым словом не найдены.")
    await state.clear()  # Очистка состояния


@dp.callback_query(add_Book.nw_genre)
async def callback_query_add_book(
        call: types.CallbackQuery,
        state: FSMContext):
    if call.data:
        # Сохранение выбранного жанра
        await state.update_data(nw_genre=call.data)
        data = await state.get_data()  # Получение всех данных о новой книге
        # Добавление новой книги в базу данных
        await db.new_book(call.from_user.id, data["nw_title"], data["nw_author"], data["nw_description"], data["nw_genre"])
        # Сообщение об успешном добавлении книги
        await bot.send_message(call.from_user.id, "Книга успешно добавлена")
        await state.clear()  # Очистка состояния


async def main():
    user = await bot.get_me()  # Получение информации о боте
    print(user.username)  # Вывод имени пользователя бота
    await dp.start_polling(bot)  # Запуск бота

if __name__ == '__main__':
    # Запуск основной функции, если файл запущен как основная программа
    asyncio.run(main())
