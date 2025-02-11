import unittest
import psycopg2 as pg
import os

class BaseTestClass(unittest.TestCase):
    @classmethod
    def connect_db(cls):
        return pg.connect(os.getenv('TEST_DATABASE_URL'))