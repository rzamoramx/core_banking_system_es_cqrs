import os

MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')
MONGO_URL = f'mongodb://{MONGO_HOST}:27017/'
MONGO_DB_NAME = 'mydb'
MONGO_BALANCE_COLLECTION = 'balance'
MONGO_USER_COLLECTION = 'user'
MONGO_TRANSACTION_COLLECTION = 'transactions'
MONGO_ACCOUNT_COLLECTION = 'account'