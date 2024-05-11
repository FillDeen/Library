import sqlite3 as sq
from collections import Counter

# Подключение к базе данных SQLite с именем файла books_users.dp
db = sq.connect(f"database/books_users.dp")
# Создание объекта курсора для выполнения SQL-запросов
cur = db.cursor()

# Асинхронная функция для создания таблицы в базе данных для каждого
# пользователя


async def db_start(user_id):
    # SQL-запрос для создания таблицы с уникальным именем для каждого
    # пользователя, если она еще не существует
    cur.execute(f"CREATE TABLE IF NOT EXISTS `{user_id}`("
                # Столбец id_book с автоинкрементом для уникального
                # идентификатора книги
                "id_book INTEGER PRIMARY KEY AUTOINCREMENT, "
                "Title TEXT, "  # Столбец Title для названия книги
                "Author TEXT, "  # Столбец Author для имени автора
                "Description TEXT, "  # Столбец Description для описания книги
                "Genre TEXT) ")  # Столбец Genre для жанра книги
    # Подтверждение транзакции
    db.commit

# Асинхронная функция для добавления новой книги в базу данных пользователя


async def new_book(user_id, title, author, description, genre):
    # Поиск книги с таким же названием в базе данных пользователя
    book = cur.execute(
        f"SELECT * FROM `{user_id}` WHERE Title == '{title}'").fetchone()
    # Если книга не найдена, добавляем новую запись
    if not book:
        cur.execute(
            f"INSERT INTO `{user_id}` (Title, Author, Description, Genre) VALUES ('{title}', '{author}','{description}','{genre}')")
    # Подтверждение транзакции
    db.commit()

# Асинхронная функция для поиска книг по ключевому слову в названии или авторе


async def search_books_by_word(user_id, word):
    # SQL-запрос для поиска книг, содержащих ключевое слово в названии или
    # имени автора
    cur.execute(
        f"SELECT Title, Author FROM `{user_id}` WHERE Title LIKE '%{word}%' OR Author LIKE '%{word}%'")
    # Получение всех подходящих записей
    books = cur.fetchall()
    # Подтверждение транзакции
    db.commit()
    # Возвращение списка найденных книг
    return books

# Асинхронная функция для получения списка всех книг пользователя


async def list_books(user_id):
    # SQL-запрос для получения списка всех книг пользователя
    cur.execute(f"SELECT id_book, Title, Author FROM `{user_id}`")
    # Получение всех записей
    books = cur.fetchall()
    # Подтверждение транзакции
    db.commit()
    # Возвращение списка книг
    return books

# Асинхронная функция для поиска книги по уникальному идентификатору


async def search_book_by_id(user_id, id_book):
    # SQL-запрос для поиска книги по идентификатору
    cur.execute(
        f"SELECT Title, Author, Description, Genre FROM `{user_id}` WHERE id_book LIKE '{id_book}'")
    # Получение всех подходящих записей
    book = cur.fetchall()
    # Подтверждение транзакции
    db.commit()
    # Возвращение информации о книге
    return book

# Асинхронная функция для поиска книг по жанру


async def search_by_genre(user_id, genre):
    # SQL-запрос для поиска книг по жанру
    cur.execute(
        f"SELECT Title, Author, Description, Genre FROM `{user_id}` WHERE Genre LIKE '{genre}'")
    # Получение всех подходящих записей
    books = cur.fetchall()
    # Подтверждение транзакции
    db.commit()
    # Возвращение списка книг по жанру
    return books

# Асинхронная функция для удаления книги по идентификатору


async def del_book(user_id, id_book):
    try:
        # SQL-запрос для удаления книги по идентификатору
        cur.execute(f'DELETE FROM `{user_id}` WHERE id_book == "{id_book}"')
        # Подтверждение транзакции
        db.commit()
    except Exception as e:
        # Откат транзакции в случае ошибки
        db.rollback()
        # Вывод сообщения об ошибке
        print(f"Произошла ошибка: {e}")

# Асинхронная функция для получения трех самых популярных жанров


async def get_all_genres(user_id):
    # SQL-запрос для получения всех жанров из базы данных пользователя
    cur.execute(f"SELECT Genre FROM `{user_id}`")
    # Получение всех записей
    genres = cur.fetchall()
    # Преобразование списка кортежей в список строк
    genres = [genre[0] for genre in genres]
    # Подтверждение транзакции
    db.commit()
    # Использование Counter для подсчета количества каждого жанра
    top_three_genres = [word for word, count in Counter(genres).most_common(3)]
    # Возвращение трех самых популярных жанров
    return top_three_genres

# Асинхронная функция для получения всех идентификаторов книг пользователя


async def get_all_id_book(user_id):
    # SQL-запрос для получения всех идентификаторов книг
    cur.execute(f"SELECT id_book FROM `{user_id}`")
    # Получение всех записей
    id_books = cur.fetchall()
    # Преобразование списка кортежей в список строк
    id_books = [id_book[0] for id_book in id_books]
    # Подтверждение транзакции
    db.commit()
    # Возвращение списка идентификаторов книг
    return id_books
