#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
import psycopg2

load_dotenv(override=True)

dsn = os.environ.get('DATABASE_URL')
if not dsn:
    print('ERROR: DATABASE_URL not set in environment')
    sys.exit(1)

schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
if not os.path.exists(schema_path):
    print(f'ERROR: schema.sql not found at {schema_path}')
    sys.exit(1)

with open(schema_path, 'r', encoding='utf-8') as f:
    sql = f.read()

print('Connecting to database...')
try:
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    cur = conn.cursor()
    print('Applying schema...')
    cur.execute(sql)
    print('Schema applied successfully.')
    cur.close()
    conn.close()
except Exception as e:
    print('Failed to apply schema:', e)
    sys.exit(2)
#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
import psycopg2

load_dotenv(override=True)

dsn = os.environ.get('DATABASE_URL')
if not dsn:
    print('ERROR: DATABASE_URL not set in environment')
    sys.exit(1)

schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
if not os.path.exists(schema_path):
    print(f'ERROR: schema.sql not found at {schema_path}')
    sys.exit(1)

with open(schema_path, 'r', encoding='utf-8') as f:
    sql = f.read()

print('Connecting to database...')
try:
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    cur = conn.cursor()
    print('Applying schema...')
    cur.execute(sql)
    print('Schema applied successfully.')
    cur.close()
    conn.close()
except Exception as e:
    print('Failed to apply schema:', e)
    sys.exit(2)
