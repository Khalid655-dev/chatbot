import mysql.connector

try:
    # Create a MySQL database connection
    cnx = mysql.connector.connect(user='root', password="Khalid@123",
                                  host='localhost', database='weightbuddy')
    cursor = cnx.cursor()

    # Create a table to store the conversation records
    table_name = 'food_lookup_conversations'
    create_table_query = """
    CREATE TABLE IF NOT EXISTS {} (
      id INT AUTO_INCREMENT PRIMARY KEY,
      query_text VARCHAR(255),
      food_name VARCHAR(255),
      calories INT,
      full_nutrients TEXT,
      protein FLOAT,
      total_fat FLOAT,
      total_carbohydrate FLOAT
    )
    """.format(table_name)

    cursor.execute(create_table_query)

    # Create a table to store the search results
    table_name = 'food_search_results'
    create_table_query2 = """
    CREATE TABLE IF NOT EXISTS {} (
      id INT AUTO_INCREMENT PRIMARY KEY,
      query_text VARCHAR(255),
      food_name VARCHAR(255),
      serving_unit VARCHAR(255)
    )
    """.format(table_name)

    cursor.execute(create_table_query2)
    cnx.commit()

except mysql.connector.Error as error:
    print("Failed to create tables in MySQL: {}".format(error))

finally:
    # Close the MySQL connection
    cursor.close()
    cnx.close()
