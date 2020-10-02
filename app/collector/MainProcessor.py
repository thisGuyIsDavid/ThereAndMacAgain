#!/usr/bin/env python
from app.databases.SQLiteProcessor import SQLiteProcessor


class MainProcessor:

    def __init__(self, database_location):
        # set SQLite processor
        self.sqlite_processor = SQLiteProcessor(database_location=database_location, run_setup=True)

    def process(self, to_process):
        self.sqlite_processor.insert_into_sqlite(to_process)
