from flask import Flask, render_template, request, redirect, session
import mysql.connector
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL database connection configuration
db_config = {
    'host': 'icram.mysql.pythonanywhere-services.com',
    'user': 'icram',
    'password': 'wD._y&v%??WfF99',
    'database': 'icram$User_Data'
}


def create_weight_entries_table():
    # Connect to the MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Create the 'weight_entries' table if it doesn't exist
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS weight_entries (
      id INT AUTO_INCREMENT PRIMARY KEY,
      user_id INT,
      weight DECIMAL(5, 2),
      date DATE,
      FOREIGN KEY (user_id) REFERENCES users(id)
    );
    '''
    cursor.execute(create_table_query)
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()


@app.route('/')
def welcome():
    return render_template('welcome.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get user data from the registration form
        username = request.form['username']
        password = request.form['password']

        # Connect to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Insert user data into the 'users' table
        insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        data = (username, password)
        cursor.execute(insert_query, data)
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get user data from the login form
        username = request.form['username']
        password = request.form['password']

        # Connect to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Retrieve user data from the 'users' table
        select_query = "SELECT * FROM users WHERE username = %s AND password = %s"
        data = (username, password)
        cursor.execute(select_query, data)
        user = cursor.fetchone()

        if user:
            # Store the user's ID in the session
            session['user_id'] = user[0]

            # Close the cursor and connection
            cursor.close()
            connection.close()

            return redirect('/dashboard')
        else:
            error = "Invalid username or password"
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' in session:
        try:
            # Connect to the MySQL database
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            # Create the 'weight_entries' table if it doesn't exist
            create_weight_entries_table()

            # Retrieve the user's data from the 'users' table
            select_query = "SELECT * FROM users WHERE id = %s"
            data = (session['user_id'],)
            cursor.execute(select_query, data)
            user = cursor.fetchone()

            if request.method == 'POST':
                weight = request.form['weight']

                # Insert weight entry into the 'weight_entries' table
                insert_query = "INSERT INTO weight_entries (user_id, weight, date) VALUES (%s, %s, %s)"
                data = (session['user_id'], weight, date.today())
                cursor.execute(insert_query, data)
                connection.commit()

            # Retrieve weight entries for the user
            select_query = "SELECT * FROM weight_entries WHERE user_id = %s"
            data = (session['user_id'],)
            cursor.execute(select_query, data)
            weight_entries = cursor.fetchall()

            # Close the cursor and connection
            cursor.close()
            connection.close()

            return render_template('dashboard.html', user=user, weight_entries=weight_entries)
        except mysql.connector.Error as error:
            print("Error retrieving data from MySQL table:", error)
            return redirect('/login')
    else:
        return redirect('/login')

@app.route('/record_weight', methods=['POST'])
def record_weight():
    if 'user_id' in session:
        try:
            weight = request.form['weight']

            # Connect to the MySQL database
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            # Insert weight entry into the 'weight_entries' table
            insert_query = "INSERT INTO weight_entries (user_id, weight, date) VALUES (%s, %s, %s)"
            data = (session['user_id'], weight, date.today())
            cursor.execute(insert_query, data)
            connection.commit()

            # Close the cursor and connection
            cursor.close()
            connection.close()

            return redirect('/dashboard')
        except mysql.connector.Error as error:
            print("Error recording weight in MySQL table:", error)
            return redirect('/dashboard')
    else:
        return redirect('/login')

@app.route('/delete_weight', methods=['POST'])
def delete_weight():
    if 'user_id' in session:
        weight_id = request.form['weight_id']

        try:
            # Connect to the MySQL database
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            # Delete the weight entry from the 'weight_entries' table
            delete_query = "DELETE FROM weight_entries WHERE id = %s"
            data = (weight_id,)
            cursor.execute(delete_query, data)
            connection.commit()

            # Close the cursor and connection
            cursor.close()
            connection.close()

            return redirect('/dashboard')
        except mysql.connector.Error as error:
            print("Error deleting weight entry:", error)

    return redirect('/login')

@app.route('/sunday_report')
def weekly_report():
    if 'user_id' in session:
        try:
            # Connect to the MySQL database
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            # Calculate the start and end dates of the previous week
            today = date.today()
            last_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
            previous_sunday = last_sunday - timedelta(days=6)  # Adjust for a full week

            # Retrieve weight entries for the previous week
            select_query = "SELECT * FROM weight_entries WHERE user_id = %s AND date >= %s AND date <= %s"
            data = (session['user_id'], previous_sunday, last_sunday)
            cursor.execute(select_query, data)
            weight_entries = cursor.fetchall()

            # Calculate the sum of weights and count of entries
            sum_of_weights = sum(entry[2] for entry in weight_entries)
            count_of_entries = len(weight_entries)

            # Perform division only if there is data
            if count_of_entries > 0:
                result = sum_of_weights / count_of_entries
            else:
                result = None

            # Close the cursor and connection
            cursor.close()
            connection.close()

            return render_template('weekly_report.html', result=result)
        except mysql.connector.Error as error:
            print("Error retrieving data from MySQL table:", error)
            return redirect('/login')
    else:
        return redirect('/login')



if __name__ == '__main__':
    app.run(debug=True)
