import mysql.connector 
import json

connection = mysql.connector.connect(
    host='localhost',
    user='ohgiraffers',
    password='ohgiraffers',
    database='carmesamadb'    
) 
sql = 'INSERT INTO tbl_car(REG_ID, CAR, YEAR) VALUES(%s, %s, %s)'

cursor = connection.cursor()


filename = f'data\\car.json'
with open(filename, encoding='utf-8') as json_file:
    json_data = json.load(json_file)

    for row in json_data:
        region_id = row['REG_ID']
        car = row['CAR']
        year = row['YEAR']

        cursor.execute(sql, (region_id, car, year))

connection.commit()
cursor.close()
connection.close()