import sqlite3

DATABASE_FILE = "plinko.db"  #  Укажи имя своего файла

def print_table(table_name):
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table_name}")  #  Выбираем все данные из таблицы
        rows = cursor.fetchall()

        print(f"\n=== Table: {table_name} ===")
        if rows:
            #  Печатаем заголовки столбцов
            print(", ".join(rows[0].keys()))

            #  Печатаем данные
            for row in rows:
                print(", ".join(str(row[key]) for key in row.keys()))
        else:
            print("Table is empty.")

    except Exception as e:
        print(f"Error reading table {table_name}: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print_table("users")  #  Выводим таблицу users
    print_table("invoices")  #  Выводим таблицу invoices
    print_table("transactions") # Выводим таблицу transactions