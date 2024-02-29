import psycopg2


# подключение к нашей базе
conn = psycopg2.connect("""
    host=rc1d-9cjee2y71olglqhg.mdb.yandexcloud.net
    port=6432
    sslmode=verify-full
    dbname=sch58_db
    user=Admin
    password=atdhfkm2024
    target_session_attrs=read-write
""")

# посылаем запрос на подключение к конкретной таблице
request = 'SELECT * FROM "Orange Galactic Empire"."Planets"'

# уснанавливаем связь с базой для выполнения запросов
cursor = conn.cursor()

# выполняем запрос
cursor.execute(request)

# табличку после запроса
data = cursor.fetchall()
print(data)

request_update = 'UPDATE "Orange Galactic Empire"."Planets" SET "Name"=\'Earth\', "System"=2, "Population"=10000000, "Leader"=\'John Wick\', "Type"=2 WHERE id=2'

# выполняем запрос
cursor.execute(request_update)
cursor.execute(request)

# сохраняем изменения обновленной таблички
conn.commit()
data = cursor.fetchall()
print(data)

request_insert = 'INSERT INTO "Orange Galactic Empire"."Planets" ("Name", "Leader", "Type", "System", "Population", "id") VALUES (\'Orange_planet\', \'Iron Man\', 2, 1, 7, DEFAULT)'

# выполняем запрос
cursor.execute(request_insert)
cursor.execute(request)

data = cursor.fetchall()
print(data)

planet_name = input("Введите название планеты, на которой произойдет рагнарек ")

request_update = f'UPDATE "Orange Galactic Empire"."Planets" SET "Name"=\'{planet_name}\', "System"=2, "Population"= 1, "Leader"=\'John Wick\', "Type"=2 WHERE "Name"= \'{planet_name}\' '

cursor.execute(request_update)
cursor.execute(request)

conn.commit()

data = cursor.fetchall()
print(data)