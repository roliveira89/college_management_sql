import mysql.connector as mysql

# Initialize database
db = mysql.connect(host="localhost",user="root",password="",database="project")
# Cursos to allow different queries (delete, insert, edit, etc)
command_handler = db.cursor(buffered=True) # Run multiple queries without errors

# Main menu
def main():
    while True: # Infinite loop
        print("Welcome to the project system. Please choose an option:")
        print("1. Login as student")
        print("2. Login as teacher")
        print("3. Login as admin")
        print("4. Exit")

        user_option = input(str("Option: "))
        if user_option == "1":
            authorize_student()
        elif user_option == "2":
            authorize_teacher()
        elif user_option == "3":
            authorize_admin()
        elif user_option == "4":
            print("Goodbye")
            break
        else:
            print("Invalid option selected")
            print("Please enter a number from 1 to 4.")
            print()
        

def authorize_student():
    print()
    print("Student's Login")
    username = input(str("Username: "))
    password = input(str("Password: "))
    # Store variables username, password and privilege into the database
    query_vals = (username, password, "student")
    # Object to run commands/queries on the SQL database
    # Insert values into the fields of the created table (users) with 'students' level privilege
    command_handler.execute("SELECT username FROM users WHERE username = %s AND password = %s AND privilege = %s",query_vals)
    # If no rows are affected (user doesn't exist), print message
    if command_handler.rowcount <= 0:
        print("Invalid login details")
        print()
    else:
        student_session(username)


def student_session(username):
    # Create the username variable because multiple values need to be passed into a query
    # The coma is a trick to avoid an error
    username = (str(username),)
    while True:
        print()
        print("Student's Menu")
        print("1. View Register")
        print("2. Download Register")
        print("3. Logout")

        user_option = input(str("Option: "))
        if user_option == "1":
            print()
            print("Displaying register")
            # Find info on the student's user table to view register
            command_handler.execute("SELECT date, username, status FROM attendance WHERE username = %s",username)
            # Fetch all the records returned from the query above
            records = command_handler.fetchall()
            # Loop to display records
            for record in records:
                print(record)
        elif user_option == "2":
            print()
            print("Downloading Register")
            command_handler.execute("SELECT date, username, status FROM attendance WHERE username = %s",username)
            records = command_handler.fetchall()
            for record in records:
                with open("register.txt", "w") as records_file:
                    records_file.write(str(records)+"\n")
            print("All records saved")
        elif user_option == "3":
            print()
            break
        else:
            print("No valid option selected")


def authorize_teacher():
    print()
    print("Teacher's Login")
    username = input(str("Username: "))
    password = input(str("Password: "))
    query_vals = (username, password)
    # Select everything (*) from users table
    command_handler.execute("SELECT * FROM users WHERE username = %s AND password = %s AND privilege = 'teacher'",query_vals)
    if command_handler.rowcount <= 0:
        print("Login not recognized")
        print()
    else:
        teacher_session()


def teacher_session():
    while True:
        print()
        print("Teacher's Menu")
        print("1. Mark student register")
        print("2. View register")
        print("3. Logout")
    
        user_option = input(str("Option: "))
        if user_option == "1":
            print()
            print("Mark student register")
            # Find names of students on user table to mark presence os absence
            command_handler.execute("SELECT username FROM users WHERE privilege = 'student'")
            # Fetch all the records returned from the query above
            records = command_handler.fetchall()
            # Date where the user will store the records
            date = input(str("Date (DD/MM/YYYY): "))
            # Loop to display the records
            for record in records:
                # Record returned as a tuple. Strip it to return just the name and not other characters
                record = str(record).replace("'","")
                record = str(record).replace(",","")
                record = str(record).replace("(","")
                record = str(record).replace(")","")
                # Status = Present(P) | AbsentA) | Late(L)
                status = input(f"Status for {str(record)} (P/A/L): ")
                # Create new variable to insert all values into the attendance table
                query_vals = (str(record),date,status)
                command_handler.execute("INSERT INTO attendance (username, date, status) VALUES(%s,%s,%s)",query_vals)
                # Save and refresh changes
                db.commit()
                print(f"{record} marked as {status}")
        elif user_option == "2":
            print()
            print("Viewing all student registers")
            command_handler.execute("SELECT username, date, status FROM attendance")
            records = command_handler.fetchall()
            print("Displaying all registers")
            for record in records:
                print(record)
        elif user_option == "3":
            print()
            break
        else:
            print("No valid option selected")


def authorize_admin():
    print()
    print("Admin Login")
    username = input(str("Username: "))
    password = input(str("Password: "))
    if username == "admin":
        if password == "password":
            admin_session()
        else:
            print("Incorrect password")
            print()
    else:
        print("Login details not recognised")
        print()


def admin_session():
    while True: # Loop the menu until user's logout
        print()
        print("Admin Menu")
        print("1. Register New Student")
        print("2. Register New Teacher")
        print("3. Delete Existing Student")
        print("4. Delete Existing Teacher")
        print("5. Logout")

        user_option = input(str("Option: "))
        if user_option == "1":
            print()
            print("Register New Student")
            username = input(str("Student username: "))
            password = input(str("Student password: "))
            # Store variables username and password into the database
            query_vals = (username,password)
            # Object to run commands/queries on the SQL database
            # Insert values into the fields of the created table (users) with 'students' level privilege
            command_handler.execute("INSERT INTO users (username,password,privilege) VALUES (%s,%s,'student')",query_vals)
            # Save the changes to the database
            db.commit()
            print(f"{username} has been registered as a student")
        
        elif user_option == "2":
            print()
            print("Register New Teacher")
            username = input(str("Teacher username: "))
            password = input(str("Teacher password: "))
            query_vals = (username,password)
            command_handler.execute("INSERT INTO users (username,password,privilege) VALUES (%s,%s,'teacher')",query_vals)
            db.commit()
            print(f"{username} has been registered as a teacher")
    
        elif user_option == "3":
            print()
            print("Delete Existing Student Account")
            username = input(str("Student username: "))
            # Second parameter is to delete just student with that username, in case there is a teacher with that same username
            query_vals = (username,"student")
            command_handler.execute("DELETE FROM users WHERE username = %s AND privilege = %s ",query_vals)
            db.commit()
            # If no rows are affected (no records deleted or user doesn't exist), print message
            if command_handler.rowcount < 1:
                print("User not found")
            else:
                print(f"{username} has been deleted")

        elif user_option == "4":
            print()
            print("Delete Existing Teacher Account")
            username = input(str("Teacher username: "))
            query_vals = (username,"teacher")
            command_handler.execute("DELETE FROM users WHERE username = %s AND privilege = %s ",query_vals)
            db.commit()
            if command_handler.rowcount < 1:
                print("User not found")
            else:
                print(f"{username} has been deleted")

        elif user_option == "5":
            break
        else:
            print("No valid option selected")


# Call main to start this program.
if __name__ == "__main__":
    main()