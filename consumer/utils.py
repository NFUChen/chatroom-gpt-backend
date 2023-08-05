import pymysql

# Replace these values with your actual database connection details
DB_HOST = 'mysql'
DB_USER = 'root'
DB_PASSWORD = 'chatchat-admin'
DB_NAME = 'db'

def read_sql_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()
def create_all_tables() -> None:
    try:
        # Connect to the database
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            # Read SQL statements from the file
            sql_statements = read_sql_file('models.sql').split(";")
            for statment in sql_statements:
                if len(statment) == 0:
                    return
                print(statment)
                # Execute SQL statements
                cursor.execute(f"{statment};")

        # Commit the changes to the database
        connection.commit()
    except pymysql.Error as error:
        print(f"Error: {error}")
    
if __name__ == "__main__":
    create_all_tables()