from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
import pygal
from pymongo import MongoClient
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from pygal.style import DarkStyle
import csv

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretivekey"
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)

# Specify the path to your CSV file
csv_file_path = r"C:\ML_project\dataset.csv"

# Initialize empty lists to store data for each column
names = []
ages = []
genders = []
areas = []
dropouts = []
cast = []
nationality = []

# Open the CSV file
with open(csv_file_path, mode='r', newline='') as file:
    # Create a CSV reader object
    csv_reader = csv.reader(file)

    # Skip the header row
    next(csv_reader)

    # Iterate over each row in the CSV file
    for row in csv_reader:
        # Extract data from each row and append to respective lists
        names.append(row[0])
        ages.append(int(row[1]))
        genders.append(row[2])
        areas.append(row[3])
        cast.append(row[4])  # Make sure to append data to the 'cast' list
        nationality.append(row[5])  # Make sure to append data to the 'nationality' list
        dropouts.append(row[6])  # Make sure to append data to the 'dropouts' list

# Construct the data dictionary
data = {
    'name': names,
    'age': ages,
    'gender': genders,
    'area': areas,
    'cast': cast,
    'nationality': nationality,
    'dropout': dropouts
}

# Print the constructed data dictionary
df = pd.DataFrame(data)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'email': request.form['email']})

    if login_user:
        if login_user['password'] == request.form['password']:
            session['email'] = request.form['email']
            return render_template('index.html')

    return 'Invalid email/password combination'

@app.route('/signup', methods=['POST'])
def signup():
    users = mongo.db.users
    existing_user = users.find_one({'email': request.form['email']})

    if existing_user is None:
        if request.form['password'] == request.form['confirm_password']:
            users.insert_one({'email': request.form['email'], 'password': request.form['password']})
            session['email'] = request.form['email']
            return redirect(url_for('dashboard'))
        else:
            return 'Passwords do not match'
    else:
        return 'Email already exists!'

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        return 'Logged in as ' + session['email']
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('aboutus.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/submit_contact_form', methods=['POST'])
def submit_contact_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']

        contact_collection = mongo.db.contacts
        contact_collection.insert_one({
            'name': name,
            'email': email,
            'phone': phone,
            'message': message
        })

        return 'Form submitted successfully!'
    else:
        return 'Error: Invalid request method'

model = RandomForestClassifier()

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user input from the form
        age_input = request.form.get('age')
        gender = request.form.get('gender')
        area = request.form.get('area')
        cast = request.form.get('cast')
        nationality = request.form.get('nationality')

        # Check if at least one of the fields is provided
        if not (age_input or gender or area):
            return "Please provide at least one input (age, gender, or area)."

        try:
            # Convert age to integer if provided
            if age_input:
                age = int(age_input)
        except ValueError:
            return "Age must be a valid number."

        # Filter the dataset based on user inputs
        analysis_df = df[((df['age'] == age) if 'age' in locals() else False) |
                         ((df['gender'] == gender) if gender else False) |
                         ((df['cast'] == cast) if cast else False) |
                         ((df['nationality'] == nationality) if nationality else False) |
                         ((df['area'] == area) if area else False)]

        # Filter the dataset further based on dropout value
        dropout_df = analysis_df[analysis_df['dropout'] == 'Yes']

        # Generate the analysis table
        analysis_table = dropout_df.to_html(index=False)
        # Generate charts based on different parameters
        gender_chart = generate_chart(dropout_df, 'gender', 'Gender Distribution')
        age_chart = generate_chart(dropout_df, 'age', 'Age Distribution')
        area_chart = generate_chart(dropout_df, 'area', 'Area Distribution')
        cast_chart = generate_chart(dropout_df, 'cast', 'Cast Distribution')
        nationality_chart = generate_chart(dropout_df, 'nationality', 'Nationality Distribution')

        # Render the charts and table in the analysis template
        return render_template('analysis.html', table=analysis_table, gender_chart=gender_chart,
                               age_chart=age_chart, area_chart=area_chart, cast_chart=cast_chart,
                               nationality_chart=nationality_chart)
    else:
        return render_template('index.html')


def generate_chart(data, column, title):
    counts = data[column].value_counts()
    chart = pygal.Bar(style=DarkStyle)
    chart.title = title
    for label, count in counts.items():
        # Convert the label to a string
        label_str = str(label)
        chart.add(label_str, count)
    return chart.render_data_uri()


if __name__ == '__main__':
    app.run(debug=True)
