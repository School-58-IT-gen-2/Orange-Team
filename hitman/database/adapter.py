import psycopg2
import csv

class AdapterDB:
    def __init__(self) -> None:
        self.conn = self.__get_connect()
        self.random = 0

    def __get_connect(self):
        """подключение к нашей базе"""
        try:
            conn = psycopg2.connect(
                """
				host=rc1d-9cjee2y71olglqhg.mdb.yandexcloud.net
				port=6432
                sslmode=verify-full
				dbname=sch58_db
				user=Admin
				password=atdhfkm2024
				target_session_attrs=read-write
			"""
            )
            return conn
        except:
            print("connection error")

    def get_all(self, table_name: str):
        """посылаем запрос на подключение к конкретной таблице"""
        request = f'SELECT * FROM "{table_name.split('.')[0]}"."{table_name.split('.')[1]}"'
        cursor = self.conn.cursor()
        cursor.execute(request)
        data = cursor.fetchall()
        return data

    def get_by_id(self, table_name: str, id: int):
        request = f'SELECT * FROM "{table_name.split('.')[0]}"."{table_name.split('.')[1]}" WHERE id = {id}'
        cursor = self.conn.cursor()
        cursor.execute(request)
        data = cursor.fetchall()
        return data
    
    def get_by_sql(self, selection: str):
        request = f'{selection}'
        cursor = self.conn.cursor()
        cursor.execute(request)
        data = cursor.fetchall()
        return data
    
    def update_by_id(self, table_name: str, update: str, id: int):
        update_param = update.split('=')[0]
        update_value = update.split('=')[1]
        request = f'UPDATE "{table_name.split('.')[0]}"."{table_name.split('.')[1]}" SET "{update_param}"=\'{update_value}\' WHERE "user_id" = {id}'
        cursor = self.conn.cursor()
        cursor.execute(request)
        self.conn.commit()
        request = f'SELECT * FROM "{table_name.split('.')[0]}"."{table_name.split('.')[1]}"'
        cursor = self.conn.cursor()
        cursor.execute(request)
        data = cursor.fetchall()
        return data
    
    def delete_by_id(self, table_name: str, id: int):
        request = f'DELETE FROM "{table_name.split('.')[0]}"."{table_name.split('.')[1]}" WHERE id = {id}'
        cursor = self.conn.cursor()
        cursor.execute(request)
        self.conn.commit()
        request = f'SELECT * FROM "{table_name.split('.')[0]}"."{table_name.split('.')[1]}"'
        cursor = self.conn.cursor()
        cursor.execute(request)
        data = cursor.fetchall()
        return data
    
    def insert(self, table_name: str, insert_data: list):
        columns = ''
        values = ''
        for i in insert_data:
            z = i.split('=')[0]
            y = i.split('=')[1]
            columns += f'"{z}", '
            values += f'\'{y}\', '
        columns = columns[:-2]
        values = values[:-2]
        request = f'INSERT INTO "{table_name.split('.')[0]}"."{table_name.split('.')[1]}" ({columns}) VALUES ({values})'
        cursor = self.conn.cursor()
        cursor.execute(request)
        self.conn.commit()
        request = f'SELECT * FROM "{table_name.split('.')[0]}"."{table_name.split('.')[1]}" '
        cursor = self.conn.cursor()
        cursor.execute(request)
        data = cursor.fetchall()
        return data
    
class CSV_read():
    def __init__(self) -> None:
        pass

    def read(self, file_root: str):
        result = []
        with open(file_root, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in reader:
                if len(row) > 1:
                    result.append(row)
        return result
    
    def insert(self, file_root: str, table_name: str, adapter: AdapterDB):
        array = self.read(file_root)
        request = []
        for i in array[1:]:
            for j in range(len(array[0])):
                request.append(f'{array[0][j]}={i[j]}')
            adapter.insert(table_name, request)
            request = []
            

a = AdapterDB()
l = CSV_read()