import time

import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Tuple, Any, Union
from config import DB_CONFIG  # конфиг с параметрами подключения


class DatabaseManager:
    def __init__(self, db_config: dict = None):
        self.db_config = db_config or DB_CONFIG

    @staticmethod
    def format_row_for_display(row: Tuple) -> str:
        """Форматированный вывод строки таблицы"""
        return '| ' + ' | '.join(map(str, row)) + ' |'

    def get_connection(self):
        """Создает и возвращает соединение с MySQL"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            return conn if conn.is_connected() else None
        except Error as e:
            print(f"Ошибка подключения к MySQL: {e}")
            return None

    def execute_query(self, query: str, params: Tuple = None,
                      fetch: bool = False, commit: bool = True) -> Optional[Union[List[Tuple], int]]:
        """
        Универсальный метод выполнения SQL-запросов
        Args:
            query: SQL запрос
            params: параметры для запроса
            fetch: если True - возвращает результат выборки
            commit: если True - подтверждает изменения

        Returns:
            List[Tuple] при fetch=True, int (количество затронутых строк) при fetch=False
        """
        conn = self.get_connection()
        if not conn:
            return None

        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())

            if fetch:
                result = cursor.fetchall()
            else:
                if commit:
                    conn.commit()
                result = cursor.rowcount

            return result

        except Exception as e:
            if not fetch and commit:
                conn.rollback()
            print(f'Ошибка при выполнении запроса: {e}')
            print(f'Запрос: {query}')
            print(f'Параметры: {params}')
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def fetch_one(self, query: str, params: Tuple = None) -> Optional[Tuple]:
        """Выполняет запрос и возвращает одну строку"""
        conn = self.get_connection()
        if not conn:
            return None

        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Exception as e:
            print(f'Ошибка при выполнении запроса: {e}')
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def fetch_all(self, query: str, params: Tuple = None) -> Optional[List[Tuple]]:
        """Выполняет запрос и возвращает все строки"""
        return self.execute_query(query, params, fetch=True)
    # def show_mech_list(self):
    #     query = 'SELECT time, problem, mechanic FROM second.main WHERE mechanic = %s;'
    #     result = self.execute_query(query, fetch=True)
    #     return result


    # def change_date_time(self, time, date):
    #     query = 'UPDATE second.main SET date = %s, time = %s WHERE id = %s;'
    #     result = self.execute_query(query, (date, time, self.id,))
    #     return result, 'correct'

    def add_good(self, title, text, price, photo, type, count):
        query = f'INSERT INTO goods (title, text, price, photo, type, count) VALUES (%s, %s, %s, %s, %s, %s)'
        result = self.execute_query(query, params=(title, text, price, photo, type, count,))
        return f"запись добавлена" if result else f'Ошибка'

    def select_actvie_ids_and_titles(self, type):
        query = 'SELECT id, title FROM goods WHERE type = %s AND count >= 1;'
        result = self.execute_query(query, params=(type, ), fetch=True)
        return result


    def show_good_by_id(self, id):
        query = 'SELECT * FROM goods WHERE id = %s;'
        result = self.execute_query(query, params=(id, ), fetch=True)
        return result

if __name__ == '__main__':
    db = DatabaseManager(DB_CONFIG)
    time_start = time.time()
    db.get_connection()



    print(time.time() - time_start)

