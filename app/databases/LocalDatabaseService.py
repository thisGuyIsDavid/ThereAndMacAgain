import mysql.connector


class LocalDatabaseService:
    current_connection = None

    def get_connection(self):
        return mysql.connector.connect(user="root", password="password", host="127.0.0.1", database="thisguyisdavid", charset='utf8')

    def insert(self, statement, values):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(statement, values)
        row_id = cursor.lastrowid
        cursor.close()
        connection.commit()
        connection.close()
        return row_id

    def get_all_rows_with_values(self, statement, values):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(statement, values)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    def get_row_with_values(self, statement, values):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(statement, values)
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result

    def get_row(self, statement):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(statement)
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result

    def get_all_rows(self, statement):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(statement)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    def insert_many(self, statement, values):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.executemany(statement, values)
        cursor.close()
        result = cursor.rowcount
        connection.commit()
        connection.close()
        return result

    def update(self, statement, value):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(statement, value)
        rows_affected = cursor.rowcount
        cursor.close()
        connection.commit()
        connection.close()
        return rows_affected

    def update_many(self, statement, values):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.executemany(statement, values)
        rows_affected = cursor.rowcount
        cursor.close()
        connection.commit()
        connection.close()
        return rows_affected

if __name__ == '__main__':
    x = LocalDatabaseService().get_all_rows("""SELECT * FROM mac_vendor_companies""")
    print(x)