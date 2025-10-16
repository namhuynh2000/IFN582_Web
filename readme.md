# Libraries to Install
Make sure to install the required libraries using the `requirements.txt` file
Run the following commands before attempting to run this code.
For Mac users, we need to do some setup before the `pip install` will work,
so we have made a seperate bash script to run instead. 

### Windows
```bash
py -m pip install -r requirements.txt
```

### macOS
You may need to find where mysqlserver has been installed for the following
script to set some flags.
To find where it may be installed at, execute the following command on
the terminal:
```bash
sudo find /usr -name mysql.h
```
Then, using what is found, we may need to update the variable named 
`mysqlhome` if it differs from our default.

```bash
chmod +x ./mac.sh && sudo ./mac.sh
```

# Database setup
Make sure to drop the old walkthrough database and execute the two SQL
files in the exercise folder. `toursite-database.sql` builds the database
and includes some data in all tables. `add-admins.sql` adds the admin table
to the database and adds one user to an admin table.

# User Accounts
There is one admin account with the following details:

```
username: admin
password: admin
```