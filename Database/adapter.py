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
        request = f'SELECT * FROM "Galactic Empire"."{table_name}"'
        cursor = self.conn.cursor()
        cursor.execute(request)
        data = cursor.fetchall()
        return data

    def get_by_id(self, table_name: str, id: int):
        request = f'SELECT * FROM "Galactic Empire"."{table_name}" WHERE id = {id}'
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
        request = f'UPDATE "Galactic Empire"."{table_name}" SET "{update_param}"=\'{update_value}\' WHERE id = {id}'
        cursor = self.conn.cursor()
        cursor.execute(request)
        self.conn.commit()
        request = f'SELECT * FROM "Galactic Empire"."{table_name}"'
        cursor = self.conn.cursor()
        cursor.execute(request)
        data = cursor.fetchall()
        return data
    
    def delete_by_id(self, table_name: str, id: int):
        request = f'DELETE FROM "Galactic Empire"."{table_name}" WHERE id = {id}'
        cursor = self.conn.cursor()
        cursor.execute(request)
        self.conn.commit()
        request = f'SELECT * FROM "Galactic Empire"."{table_name}" '
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
        request = f'INSERT INTO "Galactic Empire"."{table_name}" ({columns}) VALUES ({values})'
        cursor = self.conn.cursor()
        cursor.execute(request)
        self.conn.commit()
        request = f'SELECT * FROM "Galactic Empire"."{table_name}" '
        cursor = self.conn.cursor()
        cursor.execute(request)
        data = cursor.fetchall()
        return data
    
class CSV_read():
    def __init__(self) -> None:
        pass

    def reading(self, file_root: str):
        indata = []
        with open(file_root, 'r') as file:
            csv_reader = csv.reader(file)
            data_list = []
            for row in csv_reader:
                data_list.append(row)

        row_list = []
        for row in data_list:
            for i in range(6):
                a = data_list[0][i] + '=' + row[i]
                indata.append(a)
            row_list.append(indata)
            indata = []
        row_list.pop(0)
        print(row_list)
        return row_list
                

a = AdapterDB()
l = CSV_read()

for j in l.reading('/Users/violettailinichna/Downloads/cruisers-2.csv'):
    print(a.insert('Cruisers', j))