import mysql.connector 
import json

connection = mysql.connector.connect(
    host='localhost',
    user='ohgiraffers',
    password='ohgiraffers',
    database='carmesamadb'    
) 
sql = 'INSERT INTO tbl_population(REG_ID, YEAR, POPULATION) VALUES(%s, %s, %s)'

cursor = connection.cursor()

years = [2020, 2021, 2022, 2023, 2024]

for year in years:
    filename = f'data\\population_{year}.json'
    with open(filename, encoding='utf-8') as json_file:
        json_data = json.load(json_file)

        for row in json_data:
            reg_id = row['REG_ID']
            year = row['YEAR']
            population = row['POPULATION']

            cursor.execute(sql, (reg_id, year, population))

connection.commit()
cursor.close()
connection.close()