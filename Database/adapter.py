import psycopg2

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
            columns += f'"{i.split('=')[0]}", '
            values += f"'{i.split('=')[1]}', "
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
    
a = AdapterDB()

print(a.insert('Systems', ['Name=John', 'Star Type=black hole', 'Allegiance=Empire']))