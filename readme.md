# 🧭 HOW TO RUN THE PROJECT PROPERLY

A clear, step-by-step guide to set up and run this project on your local machine.

## ⚙️ Step 1: Install All Required Packages
Make sure you have **Python** and **pip** installed. Then install dependencies:
```bash
pip install -r requirements.txt
```

## 🗄️ Step 2: Set Up the Database
1. Open MySQL Workbench 
2. Connect to your local MySQL server.
3. Run the following SQL scripts in order:
* project.sql
* insert.sql
This creates the database schema and inserts sample data.

## 🧩 Step 3: Configure the Database Connection
Update your credentials in __init__.py:
```python
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_HOST'] = 'localhost'
```

## ▶️ Step 4: Run the Application
Start the app:
```bash
py run.py
```


Step 1: register new account role vendor

Step 1.1: vendor first
Step 1.2: Upload image
Step 1.3: in Manager page, we will remove, edit the image

Step 2.1: register new account role customer
Step 2.2: Add a new image into cart
Step 2.3: Remove image in checkout page
Step 2.4: Make a payment in checkout page

Step 3.1: Login admin account 
Step 3.2: change the role of user (customer <-> vendor)
Step 3.3: Edit category (CRUD)


