import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='datawarehouse',
    user='dwh_user',
    password='dwh_password'
)
cur = conn.cursor()
cur.execute('''
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'staging' AND table_name = 'stg_appointments'
    ORDER BY ordinal_position
''')
print('Colonnes de stg_appointments:')
for row in cur.fetchall():
    print(f'  - {row[0]}: {row[1]}')

cur.execute('SELECT * FROM staging.stg_appointments LIMIT 2')
print('\nEchantillon de donnees:')
cols = [desc[0] for desc in cur.description]
for row in cur.fetchall():
    print({col: val for col, val in zip(cols, row)})

conn.close()
