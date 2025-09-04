import mysql.connector 
import json

connection = mysql.connector.connect(
    host='localhost',
    user='ohgiraffers',
    password='ohgiraffers',
    database='carmesamadb'    
) 
sql = 'INSERT INTO tbl_region(REG_ID, REGION, SUBREGION) VALUES(%s, %s, %s)'

cursor = connection.cursor()


filename = f'data\\region.json'
with open(filename, encoding='utf-8') as json_file:
    json_data = json.load(json_file)

    for row in json_data:
        reg_id = row['REG_ID']
        region = row['REGION']
        subregion = row['SUBREGION']

        cursor.execute(sql, (reg_id, region, subregion))

connection.commit()
cursor.close()
connection.close()