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
    
        '''def get_smth(self, column: str, table_name: str):
            request = f'SELECT {column} FROM "Galactic Empire"."{table_name}"'
            cursor = self.conn.cursor()
            cursor.execute(request)
            data = cursor.fetchall()
            return data
        
        def order_by(self, selected_data: str, order_type: str):
            request = f'{selected_data} ORDER BY '
            cursor = self.conn.cursor()
            cursor.execute(request)
            data = cursor.fetchall()
            return data
        
        def where(self, condition: str):
            request = f'{selected_data} WHERE condition'
            cursor = self.conn.cursor()
            cursor.execute(request)
            data = cursor.fetchall()
            return data'''
    def get_by_sql(self, selection: str):
        request = f'{selection}'
        cursor = self.conn.cursor()
        cursor.execute(request)
        data = cursor.fetchall()
        return data
    
a = AdapterDB()

print(a.get_by_sql('SELECT * FROM "Galactic Empire"."Cruisers"'))

print(a.get_by_sql('SELECT "Name", "Star Type" FROM "Galactic Empire"."Systems" WHERE "Systems"."Allegiance"=\'Empire\' ORDER BY id ASC'))

print(a.get_by_sql('SELECT "Name", "Population" FROM "Galactic Empire"."Planets" WHERE "Planets"."Name"!=\'mityas planet\' AND "Planets"."Population">50 and "Name"=lower("Name") ORDER BY "Position" ASC'))
