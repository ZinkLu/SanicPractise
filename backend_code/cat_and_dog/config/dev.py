import getpass

from gino.dialects.asyncpg import Pool

user = getpass.getuser()

DEBUG = True
TEST = "TEST FOR CONFIG"
DATABASE_URL = "postgresql://localhost/pet_test"

DB_HOST = "localhost"
# DB_PORT
DB_USER = user
DB_PASSWORD = "123"
DB_DATABASE = "pet_test"
DB_ECHO = False
REDIS = "redis://localhost"
STATIC_PATH = "./static"

# DB_POOL_MIN_SIZE
# DB_POOL_MAX_SIZE

DB_USE_CONNECTION_FOR_REQUEST = True

DB_KWARGS = dict(
    pool_class=Pool,
)
