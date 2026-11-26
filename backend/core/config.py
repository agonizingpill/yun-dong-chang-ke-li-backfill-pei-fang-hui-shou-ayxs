import os

DATABASE_URL = os.environ['DATABASE_URL']
REDIS_URL = os.environ['REDIS_URL']
JWT_SECRET = os.environ['JWT_SECRET']
SEED_DEMO = os.getenv('SEED_DEMO', 'false').lower() == 'true'
