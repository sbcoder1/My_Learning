import mysql.connector
import getpass
from cryptography.fernet import Fernet
import re
import uuid
import os
from colorama import Fore, init
import pyfiglet
from datetime import datetime
from tabulate import tabulate
from fpdf import FPDF
from PIL import Image

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# Initialize colorama
init()

# Clear the terminal screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Display "Cinema Hub" in big text with colors
def display_cinema_hub():
    clear_screen()
    # Generate ASCII art for Cinema Hub
    ascii_art = pyfiglet.figlet_format("Cinema Hub")
    
    # Add attractive colors (green for the header, yellow for the text)
    print(Fore.GREEN + ascii_art + Fore.RESET)
    print(Fore.YELLOW + "Welcome to Movie Hub! Your ultimate destination for movie browsing, ticket booking, and more!\n" + Fore.RESET)

#-- DB CONNECTION --

db_connection = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'cinemaHub'
}

#-- Landing Menu --
def welcome_cinemahub():
    # TASK ID : 1
    options = [
        [1, "Signup/Register"],
        [2, "Login"],
        [3, "Browse"],
        [4, "Exit"]
    ]
    
    # Print the table with options
    print(tabulate(options, headers=["Option", "Action"], tablefmt="grid"))
    
    while True:
        try:
            # Input choice from user
            select_choice = int(input("\nEnter your choice [1, 2, 3, or 4]: "))
            
            if select_choice in [1, 2, 3, 4]:
                return select_choice
            else:
                print("\nInvalid Choice. Please enter 1, 2, 3, or 4.\n")
        except ValueError:
            print("\nInvalid input. Please enter a number (1, 2, 3, or 4).\n")




#Validating Code For SignUp
def validate_username(username):
    if re.fullmatch(r"^[a-zA-Z0-9]{8,15}$", username):
        return True
    else:
        print("Invalid username. Must be 8-15 alphanumeric characters and containing at least one number [a-z A-Z 0-9].")
        return False

def validate_email(email):
    '''This Function does validation of email address'''
    if re.fullmatch(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return True
    else:
        print("Invalid email format")
        return False


def validate_password(password):
    if re.fullmatch(r"^(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{8,}$", password):
        return True
    else:
        print("Invalid password. Must be at least 8 characters, containing at least one number and one special symbol [!@#$%^&*].")
        return False

#SIGNUP CODE  
def signupUser():
    print("\nSIGNUP / REGEISTER HERE")
    #username
    print("Username Must be of 8-15 alphanumeric characters and containing at least one number [a-z A-Z 0-9].")
    uname=input("Enter the UserName:")
    while not validate_username(uname):
        uname = input("Enter the UserName:")
    fname=input("Enter the First Name:")
    lname=input("Enter the Lirst Name:")
    #email
    email=input("Enter the Email Address:")
    while not validate_email(email):
        email = input("Enter your Email Address:")
    #Password
    print("Must be at least 8 characters, containing at least one number and one special symbol [!@#$%^&*].")
    passwd = getpass.getpass("Enter your password: ")
    while not validate_password(passwd):
        passwd = input("Enter your Password:")
    roles=int(input("Enter the role(admin=0 / user=1)"))
    
        
    #Encrypting Password
    key = Fernet.generate_key()
    f = Fernet(key)
    passwd = f.encrypt(passwd.encode())
    

    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        

        cursor.execute("insert into cinemahub.userinfo(username,password,fname,lname,email,encrypt_key,role) values(%s,%s,%s,%s,%s,%s,%s)",(uname,passwd,fname,lname,email,key,roles))
        print("You Regestired Succesfully ...")
        conn.commit()
        loginpage()
        conn.close()
        
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if conn.is_connected():
            cursor.close()
            conn.close()
    
#LOGIN PAGE CODE
def loginpage():
    print("Enter Your Login Details")
    username = input("\nEnter username: ")
    password = getpass.getpass("Enter your password: ")

    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        cursor.execute("SELECT password, encrypt_key, role, username FROM userinfo WHERE BINARY username = %s", (username,))
        userinputes = cursor.fetchone()

        if userinputes:
            passwd, key, role, stored_username = userinputes
            f = Fernet(key)
            decrypt_pass = f.decrypt(passwd).decode()

            if decrypt_pass == password:
                print(f"Welcome {stored_username}!")

                # Return the username after successful login
                if role == 0:  # Admin
                    adminMenu(stored_username)
                else:  # User
                    userMenu(stored_username)
                
                return stored_username  # Return the username
            else:
                print("\nIncorrect password!")
                loginpage()

        else:
            print("\nUsername not found!")
            loginpage()

        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if conn.is_connected():
            cursor.close()
            conn.close()


#USER MENU
def userMenu(username):
    print(f"Welcome user {username}")
    while True:
        menu_options = [
            ["1", "Display Theater"],
            ["2", "Display Cinema"],
            ["3", "Display Shows"],
            ["4", "Booking Seats"],
            ["5", "Cancel Booking"],
            ["0", "Exit"]
            ]

        # Display the menu in table format
        print(tabulate(menu_options, headers=["Option", "Menu"], tablefmt="fancy_grid"))

        # Get the user's choice
        userChoice = input("Enter your Option:(1-5):")

        if  userChoice== '1':
            userShowTheater()
        elif userChoice == '2':
             showCinema()
        elif userChoice == '3':
            displaySchedule()
        elif userChoice == '4':
             userBook_Seats(username)
        elif userChoice == '5':
             cancelBooking(username)
        elif userChoice == '0':
            print("You exited the CinemaHub MENU ...")
            break
        else:
            print("Invalid Choice")


#ADMIN MENU    
def adminMenu(username):
    while True:
        print(f"\nWelcome admin {username}\n")

        menu_options = [
            ["1", "Display Theater"],
            ["2", "Add Theater"],
            ["3", "Inactivate Theater"],
            ["4", "Activate Theater"],
            
            ["5", "Add Cinema"],
            ["6", "Delete Cinema"],
            ["7", "Display Cinema"],
            ["8", "Add Cinema Shows Schedules "],
            ["9", "Delete Cinema Shows Schedules "],
            ["10", "Display Cimema Shows Schedules"],
            
            ["11", "Book Seats"],
            ["12", "View Bookings"],
            ["13", "Cancel Bookings Seats"],
            ["0", "Exit"]
        ]

        # Display the menu in table format
        print(tabulate(menu_options, headers=["Option", "Menu"], tablefmt="fancy_grid"))

        # Get the user's choice
        adminch = input("Enter your Option:(0-11):")
        
        if adminch == '1':
            showTheater()
        elif adminch == '2':
            addTheater()
        elif adminch == '3':
            inactivateTheater()
        elif adminch == '4':
            activateTheater()
        elif adminch == '5':
            addCinema()
        elif adminch == '6':
            deleteCinema()
        elif adminch == '7':
            showCinema()
        elif adminch == '8':
            addCinemaShows()
        elif adminch == '9':
            deleteShows()
        elif adminch == '10':
            displaySchedule()
        elif adminch == '11':
            book_Seats()
        elif adminch == '12':
            viewBookings()
        elif adminch == '13':
            admin_cancelBooking()
        elif adminch == '0':
            print("You exited the ADMIN MENU ...")
            break
        else:
            print("Invalid Choice")


# -- THEATER SECTION CODE --

#DISPLAY InActivate THEATER           
def showTheaterInactivate():
    
    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        
        cursor.execute("SELECT theater_id,theater_name,status from cinemahub.theater Where status=\"inactive\"")
        dis_theater = cursor.fetchall()
        
        headers = ["theater_id", "theater_name" ,"Status"]
        print(tabulate(dis_theater, headers=headers, tablefmt="fancy_grid"))
        
        
        conn.commit()

        print("\nInActive Theater displayed.\n")

        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

#DISPLAY ACTIVE THEATER
def showTheater():
    
    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        
        cursor.execute("SELECT theater_id,theater_name,theater_location,theater_add_date,theater_capacity,theater_screen,status from cinemahub.theater Where status=\"active\"")
        dis_theater = cursor.fetchall()
        
        headers = ["Theater_id", "Theater_name" ,"Theater_location","Theater_add_date","Theater_capacity","Theater_screen","Status"]
        print(tabulate(dis_theater, headers=headers, tablefmt="fancy_grid"))
        
        
        conn.commit()

        print("\nTheater displayed.\n")

        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


#UserSeatsBooking
            
def userBook_Seats(username):
    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        print("\nHere are the list of all Theaters:\n")
        cursor.execute("SELECT theater_id, theater_name, theater_location, theater_screen, theater_start_time, theater_end_time FROM theater")
        theaters = cursor.fetchall()

        if not theaters:
            print("No theaters available.")
            return
        
        theater_headers = ["Theater ID", "Theater Name", "Location", "Screen Count", "Theater_start_time", "Theater_start_time"]
        print(tabulate(theaters, headers=theater_headers, tablefmt='fancy_grid'))

        selectTheaterId = input("\nEnter the Theater ID to view cinemas: ")

        cursor.execute("""
            SELECT cinema_id, cinema_name, cinema_duration, cinema_cost
            FROM cinema
            WHERE cinema_theater_uuid = (SELECT theater_uuid FROM theater WHERE theater_id = %s)
        """, (selectTheaterId,))
        cinemas = cursor.fetchall()

        if not cinemas:
            print("\nNo cinemas available for the selected Theater ID.")
            return
        
        cinema_headers = ["Cinema ID", "Cinema Name", "Duration (mins)", "Cost (INR)"]
        print(tabulate(cinemas, headers=cinema_headers, tablefmt='fancy_grid'))

        selectCinemaId = input("\nEnter the Cinema ID to view show schedule: ")

        cursor.execute("""SELECT s.show_id, t.theater_name, c.cinema_name, s.show_time, s.screen_number, s.schedule_status 
                          FROM shows s 
                          JOIN theater t ON s.theater_uuid = t.theater_uuid 
                          JOIN cinema c ON s.cinema_uuid = c.cinema_uuid 
                          WHERE t.theater_id = %s AND c.cinema_id = %s 
                          ORDER BY s.show_time""", (selectTheaterId, selectCinemaId))
        shows = cursor.fetchall()

        if shows:
            show_headers = ["Show ID", "Theater Name", "Cinema Name", "Show Time", "Screen Number", "Status"]
            print("\nScheduled Shows for the selected cinema:")
            print(tabulate(shows, headers=show_headers, tablefmt='fancy_grid'))

            selectShowId = input("\nEnter the Show ID to be Selected: ")

            cursor.execute("""
                SELECT s.show_id, s.screen_number, s.show_time, t.theater_name, c.cinema_name, s.theater_uuid, 
                       s.cinema_uuid, c.cinema_cost, t.theater_rows, t.theater_columns
                FROM shows s
                JOIN theater t ON s.theater_uuid = t.theater_uuid
                JOIN cinema c ON s.cinema_uuid = c.cinema_uuid
                WHERE s.show_id = %s
            """, (selectShowId,))
            selectedShow = cursor.fetchone()

            if selectedShow:
                print(f"\nSelected Show ID: {selectShowId} Details:")
                show_id, screen_number, show_time, theater_name, cinema_name, theater_uuid, cinema_uuid, cinema_cost, theater_rows, theater_columns = selectedShow
                selectedShowData = [[show_id, screen_number, show_time, theater_name, cinema_name]]
                print(tabulate(selectedShowData, headers=["Show ID", "Screen Number", "Show Time", "Theater Name", "Cinema Name"], tablefmt='fancy_grid'))

                # Seat Layout Display
                cursor.execute("""SELECT seat_row, seat_col FROM booked_seats WHERE show_id = %s""", (selectShowId,))
                booked_seats = cursor.fetchall()

                print("\nAvailable Seats Layout (Use [row,column] to select seats):")
                print("    ", end="")
                for col in range(1, theater_columns + 1):
                    print(f" {col:2}", end=" ")
                print()

                for row in range(1, theater_rows + 1):
                    print(f"{row:2} ", end="")
                    for col in range(1, theater_columns + 1):
                        if (row, col) in [(r[0], r[1]) for r in booked_seats]:
                            print("[X]", end=" ")
                        else:
                            print("[ ]", end=" ")
                    print()

                print("\nTo book seats, enter the format 'row,column' (e.g., 1,2) or 'done' to finish.")
                booked_seats_input = []
                total_price = 0  # Initialize total price

                while True:
                    seat = input("Enter Seat to Book or 'done' to finish: ")
                    if seat.lower() == 'done':
                        break
                    try:
                        row, col = map(int, seat.split(','))
                        if (row, col) in [(r[0], r[1]) for r in booked_seats]:
                            print("This seat is already booked. Please choose another one.")
                        else:
                            booked_seats_input.append((row, col))
                            total_price += cinema_cost  # Dynamically add price based on the selected cinema's cost
                    except ValueError:
                        print("Invalid input format. Please use 'row,column'.")

                # Generate the ticket after booking seats

                ticket_id = str(uuid.uuid4())[:8]
                
                ticket_file = f"cinemahub_ticket_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
                
                generate_ticket(show_details={ 
                    "cinema_name": cinema_name,
                    "theater_name": theater_name,
                    "show_time": show_time,
                    "screen_number": screen_number,
                    "ticket_id": ticket_id 
                }, selected_seats=booked_seats_input, total_price=total_price)

                # Insert booked seats into the database, now with username
                for seat in booked_seats_input:
                    row, col = seat
                    
                    cursor.execute("""
                        INSERT INTO booked_seats (show_id, theater_uuid, cinema_uuid, seat_row, seat_col, is_booked, username,ticket_id)
                        VALUES (%s, %s, %s, %s, %s, 'yes', %s,%s)
                    """, (show_id, theater_uuid, cinema_uuid, row, col, username,ticket_id))  
                    conn.commit()

                # Show confirmation of booking
                print(f"\nYou have booked the following seats:")
                booked_seat_details = [[f"Row {seat[0]}", f"Col {seat[1]}"] for seat in booked_seats_input]
                print(tabulate(booked_seat_details, headers=["Row", "Column"], tablefmt="fancy_grid"))

                print(f"\nTotal Price for booking {len(booked_seats_input)} seat(s): ₹{total_price}")

                print("\nUpdated Available Seats Layout:")
                print("    ", end="")
                for col in range(1, theater_columns + 1):
                    print(f" {col:2}", end=" ")
                print()

                for row in range(1, theater_rows + 1):
                    print(f"{row:2} ", end="")
                    for col in range(1, theater_columns + 1):
                        if (row, col) in [(r[0], r[1]) for r in booked_seats_input]:
                            print("[X]", end=" ")
                        else:
                            print("[ ]", end=" ")
                    print()

            else:
                print("\nInvalid Show ID selected.")
        else:
            print("\nNo schedule details found for the selected Cinema.")

        while True:
            returnGuest = input("\nEnter (y) To Return to Landing Menu (n) To Exit [y/n]: ")
            if returnGuest == 'y':
                welcome_cinemahub()
                break  
            elif returnGuest == 'n':
                print("Thanks For Visiting CineHub....")
                break
            else:
                print("Invalid Choice!")
                continue

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        
#UserShowTheater
def userShowTheater():
    
    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        
        cursor.execute("SELECT theater_id,theater_name,theater_location,theater_capacity,theater_screen,theater_start_time,theater_end_time from cinemahub.theater Where status=\"active\"")
        dis_theater = cursor.fetchall()
        
        headers = ["Theater_id", "Theater_name" ,"Theater_location","Theater_capacity","Theater_screen","Theater_start_time","Theater_end_time"]
        print(tabulate(dis_theater, headers=headers, tablefmt="fancy_grid"))
        
        
        conn.commit()

        print("\nTheater displayed.\n")

        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

#userCancelBooking
def cancelBooking(username):
    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        # Display the user's booked seats first, including cinema_name
        print("\nYour Booked Seats (Use Booking ID to Cancel):")
        cursor.execute("""
            SELECT b.booking_id, b.show_id, b.seat_row, b.seat_col, b.username, c.cinema_name 
            FROM booked_seats b
            JOIN cinema c ON b.cinema_uuid = c.cinema_uuid
            WHERE b.is_booked = 'yes' AND b.username = %s
        """, (username,))
        booked_seats = cursor.fetchall()

        if not booked_seats:
            print("No booked seats found for your account.")
            return
        
        booked_seats_headers = ["Booking ID", "Show ID", "Row", "Column", "Username", "Cinema Name"]
        print(tabulate(booked_seats, headers=booked_seats_headers, tablefmt="fancy_grid"))

        # Get the Booking ID from the user for cancellation
        booking_id_to_cancel = input("\nEnter the Booking ID to Cancel: ")

        # Check if the Booking ID exists for the logged-in user
        cursor.execute("""
            SELECT booking_id 
            FROM booked_seats 
            WHERE booking_id = %s AND username = %s AND is_booked = 'yes'
        """, (booking_id_to_cancel, username))
        booking = cursor.fetchone()

        if not booking:
            print("Invalid Booking ID or the seat is not currently booked.")
            return

        # Cancel the booking (update is_booked to 'no')
        cursor.execute("""
            UPDATE booked_seats 
            SET is_booked = 'no' 
            WHERE booking_id = %s
        """, (booking_id_to_cancel,))
        conn.commit()

        print(f"Booking with ID {booking_id_to_cancel} has been successfully canceled.")

        # Display updated booked seats
        print("\nUpdated Booked Seats:")
        cursor.execute("""
            SELECT b.booking_id, b.show_id, b.seat_row, b.seat_col, b.username, c.cinema_name 
            FROM booked_seats b
            JOIN cinema c ON b.cinema_uuid = c.cinema_uuid
            WHERE b.is_booked = 'yes' AND b.username = %s
        """, (username,))
        updated_booked_seats = cursor.fetchall()

        if updated_booked_seats:
            print(tabulate(updated_booked_seats, headers=booked_seats_headers, tablefmt="fancy_grid"))
        else:
            print("No remaining booked seats for your account.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn:
            conn.close()


#ADD THEATER ...         
def addTheater():
    # Generate unique theater ID
    tid = str(uuid.uuid4())
    tname = input("Enter the Theater Name: ")
    tlocation = input("Enter the Theater Location: ")
    tscreen = input("Enter the Theater Screen available: ")
    tstatus = input("Enter the Theater Status (Open/Close): ")
    tcapacity = input("Enter the Theater Capacity: ")

    # Input for the layout (number of rows and columns)
    rows = int(input("Enter the number of rows in the Theater Layout: "))
    cols = int(input("Enter the number of columns in the Theater Layout: "))

    # Calculate the total capacity based on rows and columns
    total_capacity = rows * cols

    # Input for show timings
    tstart_time = input("Enter the Theater Start Time (e.g., 10:00 AM): ")
    tend_time = input("Enter the Theater End Time (e.g., 10:00 PM): ")

    # Get the current date and time for add date
    tadd_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        # Establish a connection to the database
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        # SQL query to insert the new theater data, including rows and columns separately
        sqlTheater = """INSERT INTO theater (theater_uuid, theater_name, theater_location, theater_screen, theater_status, theater_capacity, theater_rows, theater_columns, theater_add_date, theater_start_time, theater_end_time) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"""
        
        # Execute the query with the provided data
        cursor.execute(sqlTheater, (tid, tname, tlocation, tscreen, tstatus, total_capacity, rows, cols, tadd_date, tstart_time, tend_time))

        # Commit the transaction
        conn.commit()

        print("YOU ADDED THEATER DETAILS SUCCESSFULLY ...")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        # Close the connection and cursor properly
        if conn.is_connected():
            cursor.close()
            conn.close()

#INACTIVATE THEATER
def inactivateTheater():
    print("\nHere are the list of all Theaters. Type the Theater ID you want to inactivate:\n")
    showTheater()  
    
    inactivateTheaterId = input("Enter the Theater ID to be inactivated: ")  

    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        
        cursor.execute("SELECT theater_id, status, theater_uuid FROM theater WHERE theater_id = %s", (inactivateTheaterId,))
        result = cursor.fetchone()

        if result is None:
            print("\nTheater ID does not exist. Please enter a valid Theater ID.")
        else:
            theater_id, current_status, theater_uuid = result

            if current_status == 'inactive':
                print("\nThis theater is already inactive.")
            else:
                cursor.execute("UPDATE theater SET status = 'inactive' WHERE theater_id = %s", (inactivateTheaterId,))
            
                cursor.execute("UPDATE cinema SET status = 'inactive' WHERE cinema_theater_uuid = %s", (theater_uuid,))
                
                cursor.execute("UPDATE `shows` SET status = 'inactive' WHERE theater_uuid = %s", (theater_uuid,))
                
                conn.commit()

                cursor.execute("SELECT status FROM theater WHERE theater_id = %s", (inactivateTheaterId,))
                v_result = cursor.fetchone()

                if v_result and v_result[0] == 'inactive':
                    print("\nTheater inactivated successfully.")
                else:
                    print("\nTheater inactivation failed. Please try again.")
        
       
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()




#ACTIVATE THEATER
def activateTheater():
    print("\nHere are the list of all Theaters. Type the Theater ID you want to inactivate:\n")
    showTheaterInactivate()  
    
    activateTheaterId = input("Enter the Theater ID to be activated: ")  

    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        
        cursor.execute("SELECT theater_id, status, theater_uuid FROM theater WHERE theater_id = %s", (activateTheaterId,))
        result = cursor.fetchone()

        if result is None:
            print("\nTheater ID does not exist. Please enter a valid Theater ID.")
        else:
            theater_id, current_status, theater_uuid = result

            if current_status == 'active':
                print("\nThis theater is already active.")
            else:
                cursor.execute("UPDATE theater SET status = 'active' WHERE theater_id = %s", (activateTheaterId,))
            
                cursor.execute("UPDATE cinema SET status = 'active' WHERE cinema_theater_uuid = %s", (theater_uuid,))
                
                cursor.execute("UPDATE `shows` SET status = 'active' WHERE theater_uuid = %s", (theater_uuid,))
                
                conn.commit()

                cursor.execute("SELECT status FROM theater WHERE theater_id = %s", (activateTheaterId,))
                v_result = cursor.fetchone()

                if v_result and v_result[0] == 'active':
                    print("\nTheater activated successfully.")
                else:
                    print("\nTheater activation failed. Please try again.")
        
       
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

            
# -- CINEMA SECTION --

def addCinema():
    print("\nHere are the list of all Theaters. Type the Theater ID you want to add the Cinema for:\n")
    showTheater()  

    theater_id = input("Enter the Theater ID to add Cinema: ")

    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        cursor.execute("SELECT theater_uuid FROM theater WHERE theater_id = %s", (theater_id,))
        theater_result = cursor.fetchone()

        if theater_result is None:
            print("Theater ID does not exist. Please enter a valid Theater ID.")
        else:
            theater_uuid = theater_result[0]  
            print(f"Proceeding with the Cinema addition for Theater ID: {theater_id}")

            cinema_uuid = str(uuid.uuid4())  
            cinema_name = input("Enter the Cinema Name: ")
            cinema_title = input("Enter the Cinema Title: ")
            cinema_details = input("Enter Cinema Details: ")
            cinema_lang = input("Enter Cinema Language: ")
            cinema_date = input("Enter Cinema Date (YYYY-MM-DD): ")
            cinema_duration = input("Enter Cinema Duration (in minutes): ")
            cinema_type = input("Enter Cinema Type : ")
            cinema_cost = float(input("Enter Cinema Cost (Ticket Price): "))
            cinema_add_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

           
            sql = """INSERT INTO cinema 
                     (cinema_uuid, cinema_name, cinema_title, cinema_details, cinema_lang, cinema_date,cinema_duration, cinema_type, cinema_cost,cinema_add_date,cinema_theater_uuid)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            cursor.execute(sql, (cinema_uuid, cinema_name, cinema_title, cinema_details, cinema_lang, cinema_date, 
                                  cinema_duration, cinema_type, cinema_cost,cinema_add_date,theater_uuid))

            
            conn.commit()
            print("\nCinema Added Successfully!")

            while True:
                returnAdminMenu = input("\nEnter (y) To Return to Admin Menu or (n) To Login Menu [y/n]: ")
                if returnAdminMenu == 'y':
                    adminMenu(stored_username)
                    break  
                elif returnAdminMenu == 'n':
                    print("You Exited Admin Menu")
                    loginpage()
                    break  
                else:
                    print("Invalid input. Please enter 'y' to return to Admin Menu or 'n' to Exit.")

        
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if conn.is_connected():
            cursor.close()
            conn.close()

#DELETE CINEMA
def deleteCinema():
    print("\nHere are the list of all Cinemas. Type the Cinema ID you want to delete:\n")
    showCinema()  
    
    deleteCinemaId = input("Enter the Cinema ID to be deleted: ")

    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        cursor.execute("SELECT cinema_id FROM cinema WHERE cinema_id = %s", (deleteCinemaId,))
        result = cursor.fetchone()

        if result is None:
            print("\nCinema ID does not exist. Please enter a valid Cinema ID.")
        else:
            cursor.execute("DELETE FROM cinema WHERE cinema_id = %s", (deleteCinemaId,))
            conn.commit()

            cursor.execute("SELECT cinema_id FROM cinema WHERE cinema_id = %s", (deleteCinemaId,))
            v_result = cursor.fetchone()

            if v_result is None:
                print("\nCinema deleted successfully.\n")
            else:
                print("Cinema deletion failed. The cinema is still exists.")

        while True:
            returnAdminMenu = input("\nEnter (y) To Return to Admin Menu or (n) To Login Menu [y/n]: ")
            if returnAdminMenu == 'y':
                adminMenu(stored_username)
                break  
            elif returnAdminMenu == 'n':
                print("You Exited Admin Menu")
                loginpage()
                break  
            else:
                print("Invalid input. Please enter 'y' to return to Admin Menu or 'n' to Exit.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# SHOW CINEMA 
def showCinema():
    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        cursor.execute("SELECT cinema_id, cinema_name, cinema_title,cinema_lang,cinema_duration FROM cinema")
        dis_cinema = cursor.fetchall()

        headers = ["Cinema ID", "Cinema Name", "Cinema Title","Cinema_lang","Cinema_duration"]
        print(tabulate(dis_cinema, headers=headers, tablefmt="fancy_grid"))

        conn.commit()

        print("\nCinema displayed successfully.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


#ADD CINEMA SHOWS

def addCinemaShows():
    print("\nHere are the list of all Theaters:\n")
    showTheater()
    
    selectTheaterId = input("\nEnter the Theater ID to be Selected: ")

    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        cursor.execute("""SELECT t.theater_id, t.theater_name, c.cinema_id, c.cinema_name, c.cinema_title FROM theater t 
                          JOIN cinema c ON t.theater_uuid = c.cinema_theater_uuid WHERE t.theater_id = %s""", (selectTheaterId,))
        
        result = cursor.fetchall()

        if not result:
            print("\nNo cinema data found for the selected Theater ID. Please try again.")
        else:
            print(f"\nSelected Theater and Cinema Details for Theater ID {selectTheaterId}:\n")
            
            theater_data = []
            for row in result:
                theater_id, theater_name, cinema_id, cinema_name, cinema_title = row
                theater_data.append([theater_id, theater_name, cinema_id, cinema_name])

            headers = ["Theater ID", "Theater Name", "Cinema ID", "Cinema Name"]
            print(tabulate(theater_data, headers=headers, tablefmt='fancy_grid'))

            selectCinemaId = input("\nEnter the Cinema ID to be Selected: ")

            cursor.execute("""SELECT t.theater_id, t.theater_name, c.cinema_id, c.cinema_name 
                              FROM theater t JOIN cinema c ON t.theater_uuid = c.cinema_theater_uuid WHERE c.cinema_id = %s """, (selectCinemaId,))
            
            selectedCinemaResult = cursor.fetchone()

            if selectedCinemaResult:
                theater_id, theater_name, cinema_id, cinema_name = selectedCinemaResult
                print(f"\nSelected Cinema ID : {selectCinemaId} Details:")
                selectedCinemaData = [[theater_id, theater_name, cinema_id, cinema_name]]
                print(tabulate(selectedCinemaData, headers=["Theater ID", "Theater Name", "Cinema ID", "Cinema Name"], tablefmt='fancy_grid'))

                
                cursor.execute("""SELECT t.theater_name, t.theater_screen, t.theater_start_time, t.theater_end_time, 
                                  c.cinema_name, c.cinema_duration 
                                  FROM theater t 
                                  JOIN cinema c ON t.theater_uuid = c.cinema_theater_uuid 
                                  WHERE c.cinema_id = %s""", (selectCinemaId,))

                show_details = cursor.fetchall()

                if show_details:
                    print(f"\nShow Details for Selected Cinema ID {selectCinemaId}:\n")
                    show_data = []
                    for show in show_details:
                        theater_name, theater_screen, theater_start_time, theater_end_time, cinema_name, _cinema_duration = show
                        show_data.append([theater_name, theater_screen, theater_start_time, theater_end_time, cinema_name, _cinema_duration])

                    show_headers = ["Theater Name", "Theater Screen", "Start Time", "End Time", "Cinema Name", "Cinema Duration"]
                    print(tabulate(show_data, headers=show_headers, tablefmt='fancy_grid'))

                    scheduleShows(theater_id, cinema_id, cinema_name)
                else:
                    print("\nNo show details found for the selected Cinema.")
            else:
                print("\nInvalid Cinema ID selected.")

            

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn:
            conn.close()

#Continued
def scheduleShows(theater_id, cinema_id, cinema_name):
    try:
        
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        
        cursor.execute("""SELECT t.theater_uuid, c.cinema_uuid FROM theater t JOIN cinema c ON t.theater_uuid = c.cinema_theater_uuid WHERE t.theater_id = %s AND c.cinema_id = %s """, (theater_id, cinema_id))

        result = cursor.fetchone()

        if result:
            theater_uuid, cinema_uuid = result

            
            num_shows = int(input(f"\nEnter the number of shows for Cinema '{cinema_name}' (Cinema ID: {cinema_id}): "))

            
            for i in range(num_shows):
                print(f"\n--- Show {i+1} ---")
                start_time = input("\nEnter the Start Time for Show with Date (YYYY-MM-DD HH:MM:SS AM/PM): ")
                end_time = input("\nEnter the End Time for Show (HH:MM:SS AM/PM): ")
                screen_number = int(input("\nEnter the Screen Number: "))
                

                show_time = start_time  

                
                cursor.execute("""
                    INSERT INTO shows (theater_uuid, cinema_uuid, screen_number, show_time, schedule_status)
                    VALUES (%s, %s, %s, %s,%s)
                """, (theater_uuid, cinema_uuid, screen_number, show_time,'Scheduled'))

            
            conn.commit()

            
            print(f"\n{num_shows} shows successfully scheduled for Cinema '{cinema_name}' (Cinema ID: {cinema_id}).")
            
            
            cursor.execute("""SELECT t.theater_name, c.cinema_name, s.show_time, s.screen_number, s.schedule_status FROM shows s JOIN theater t ON s.theater_uuid = t.theater_uuid JOIN cinema c ON s.cinema_uuid = c.cinema_uuid WHERE t.theater_id = %s AND c.cinema_id = %s ORDER BY s.show_time """, (theater_id, cinema_id))

          
            shows = cursor.fetchall()

            
            if shows:
                print(f"\nScheduled Shows for Cinema '{cinema_name}' (Cinema ID: {cinema_id}):")
                show_data = []
                for show in shows:
                    theater_name, cinema_name, show_time, screen_number, status = show
                    show_data.append([theater_name, cinema_name, show_time, screen_number, status])

                show_headers = ["Theater Name", "Cinema Name", "Show Time", "Screen Number", "Status"]
                print(tabulate(show_data, headers=show_headers, tablefmt='fancy_grid'))
            else:
                print("\nNo scheduled shows found for this Cinema.")

        else:
            print("\nNo data found for the provided Theater ID and Cinema ID combination.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if conn:
            conn.close()
        
        

#DISPLAY SHOWS
def displaySchedule():
    print("\nHere are the list of all Theaters:\n")
    
    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        
        cursor.execute("SELECT theater_id, theater_name FROM theater")
        theaters = cursor.fetchall()

        if not theaters:
            print("No theaters available.")
            return
        
        
        theater_headers = ["Theater ID", "Theater Name"]
        print(tabulate(theaters, headers=theater_headers, tablefmt='fancy_grid'))

        
        selectTheaterId = input("\nEnter the Theater ID to view schedule: ")

        
        cursor.execute("""SELECT cinema_id, cinema_name FROM cinema 
                          WHERE cinema_theater_uuid = (SELECT theater_uuid FROM theater WHERE theater_id = %s)""",
                       (selectTheaterId,))
        cinemas = cursor.fetchall()

        if not cinemas:
            print("\nNo cinemas available for the selected Theater ID.")
            return
        
       
        cinema_headers = ["Cinema ID", "Cinema Name"]
        print(tabulate(cinemas, headers=cinema_headers, tablefmt='fancy_grid'))

        
        selectCinemaId = input("\nEnter the Cinema ID to view show schedule: ")

        
        cursor.execute("""SELECT t.theater_name, c.cinema_name, s.show_time, s.screen_number, s.schedule_status 
                          FROM shows s
                          JOIN theater t ON s.theater_uuid = t.theater_uuid
                          JOIN cinema c ON s.cinema_uuid = c.cinema_uuid
                          WHERE t.theater_id = %s AND c.cinema_id = %s
                          ORDER BY s.show_time""",
                       (selectTheaterId, selectCinemaId))
        shows = cursor.fetchall()

        if shows:
            show_headers = ["Theater Name", "Cinema Name", "Show Time", "Screen Number", "Status"]
            print("\nScheduled Shows for the selected cinema:")
            print(tabulate(shows, headers=show_headers, tablefmt='fancy_grid'))
        else:
            print("\nNo scheduled shows found for the selected cinema.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if conn:
            conn.close()



def deleteShows():
    print("\nDelete Shows by Selecting Theater and Cinema:\n")

    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

    
        cursor.execute("SELECT theater_id, theater_name FROM theater")
        theaters = cursor.fetchall()

        if not theaters:
            print("No theaters available.")
            return


        theater_headers = ["Theater ID", "Theater Name"]
        print(tabulate(theaters, headers=theater_headers, tablefmt='fancy_grid'))

    
        selectTheaterId = input("\nEnter the Theater ID to view schedule: ")

        
        cursor.execute("""SELECT cinema_id, cinema_name FROM cinema WHERE cinema_theater_uuid = (SELECT theater_uuid FROM theater WHERE theater_id = %s)""",(selectTheaterId,))
        cinemas = cursor.fetchall()

        if not cinemas:
            print("\nNo cinemas available for the selected Theater ID.")
            return

        cinema_headers = ["Cinema ID", "Cinema Name"]
        print(tabulate(cinemas, headers=cinema_headers, tablefmt='fancy_grid'))


        selectCinemaId = input("\nEnter the Cinema ID to display show schedule: ")

        
        cursor.execute("""SELECT s.show_id, t.theater_name, c.cinema_name, s.show_time, s.screen_number, s.schedule_status FROM shows s JOIN theater t ON s.theater_uuid = t.theater_uuid JOIN cinema c ON s.cinema_uuid = c.cinema_uuid WHERE t.theater_id = %s AND c.cinema_id = %s ORDER BY s.show_time""",(selectTheaterId, selectCinemaId))
        shows = cursor.fetchall()

        if shows:
            show_headers = ["Show ID", "Theater Name", "Cinema Name", "Show Time", "Screen Number", "Status"]
            print("\nScheduled Shows for the selected cinema:")
            print(tabulate(shows, headers=show_headers, tablefmt='fancy_grid'))
            
            deleteShowId = input("\nEnter the Show ID to delete: ")

            cursor.execute("DELETE FROM shows WHERE show_id = %s", (deleteShowId,))
            conn.commit()
            print("\nShow deleted successfully.")

        else:
            print("\nNo scheduled shows found for the selected cinema.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if conn:
            conn.close()
   
#BROWSE FUNCTION
def browse():
    print("\nHere are the list of all Theaters:\n")
    showTheater()  # Display all theaters without needing a username

    selectTheaterId = input("\nEnter the Theater ID to be Selected: ")

    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        # Fetch theater and cinema details based on the Theater ID
        cursor.execute("""SELECT t.theater_id, t.theater_name, c.cinema_id, c.cinema_name, c.cinema_title 
                          FROM theater t 
                          JOIN cinema c ON t.theater_uuid = c.cinema_theater_uuid 
                          WHERE t.theater_id = %s""", (selectTheaterId,))
        
        result = cursor.fetchall()

        if not result:
            print("\nNo cinema data found for the selected Theater ID. Please try again.")
        else:
            print(f"\nSelected Theater and Cinema Details for Theater ID {selectTheaterId}:\n")
            
            theater_data = []
            for row in result:
                theater_id, theater_name, cinema_id, cinema_name, cinema_title = row
                theater_data.append([theater_id, theater_name, cinema_id, cinema_name])

            headers = ["Theater ID", "Theater Name", "Cinema ID", "Cinema Name"]
            print(tabulate(theater_data, headers=headers, tablefmt='fancy_grid'))

            selectCinemaId = input("\nEnter the Cinema ID to be Selected: ")

            cursor.execute("""SELECT t.theater_id, t.theater_name, c.cinema_id, c.cinema_name 
                              FROM theater t 
                              JOIN cinema c ON t.theater_uuid = c.cinema_theater_uuid 
                              WHERE c.cinema_id = %s """, (selectCinemaId,))
            
            selectedCinemaResult = cursor.fetchone()

            if selectedCinemaResult:
                theater_id, theater_name, cinema_id, cinema_name = selectedCinemaResult
                print(f"\nSelected Cinema ID: {selectCinemaId} Details:")
                selectedCinemaData = [[theater_id, theater_name, cinema_id, cinema_name]]
                print(tabulate(selectedCinemaData, headers=["Theater ID", "Theater Name", "Cinema ID", "Cinema Name"], tablefmt='fancy_grid'))

                # Fetch show details for the selected cinema
                cursor.execute("""SELECT t.theater_name, t.theater_screen, t.theater_start_time, t.theater_end_time, 
                                  c.cinema_name, c.cinema_duration 
                                  FROM theater t 
                                  JOIN cinema c ON t.theater_uuid = c.cinema_theater_uuid 
                                  WHERE c.cinema_id = %s""", (selectCinemaId,))

                show_details = cursor.fetchall()

                if show_details:
                    print(f"\nShow Details for Selected Cinema ID {selectCinemaId}:\n")
                    show_data = []
                    for show in show_details:
                        theater_name, theater_screen, theater_start_time, theater_end_time, cinema_name, _cinema_duration = show
                        show_data.append([theater_name, theater_screen, theater_start_time, theater_end_time, cinema_name, _cinema_duration])

                    show_headers = ["Theater Name", "Theater Screen", "Start Time", "End Time", "Cinema Name", "Cinema Duration"]
                    print(tabulate(show_data, headers=show_headers, tablefmt='fancy_grid'))
                else:
                    print("\nNo show details found for the selected Cinema.")
            else:
                print("\nInvalid Cinema ID selected.")

            while True:
                returnGuest = input("\nEnter (y) To Return to Landing Menu, (n) To Exit [y/n]: ").lower()
                if returnGuest == 'y':
                    return True  # Indicate to return to the landing menu
                elif returnGuest == 'n':
                    print("Thanks for visiting CineHub...")
                    return False  # Indicate to exit the application
                else:
                    print("Invalid input. Please enter 'y' to return to the Landing Menu or 'n' to Exit.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn:
            conn.close()


#BOOK SEATS
def book_Seats():
    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        print("\nHere are the list of all Theaters:\n")
        cursor.execute("SELECT theater_id, theater_name, theater_location, theater_screen, theater_rows, theater_columns FROM theater")
        theaters = cursor.fetchall()

        if not theaters:
            print("No theaters available.")
            return
        
        theater_headers = ["Theater ID", "Theater Name", "Location", "Screen Count", "Rows", "Columns"]
        print(tabulate(theaters, headers=theater_headers, tablefmt='fancy_grid'))

        selectTheaterId = input("\nEnter the Theater ID to view cinemas: ")

        cursor.execute("""
            SELECT cinema_id, cinema_name, cinema_duration, cinema_cost
            FROM cinema
            WHERE cinema_theater_uuid = (SELECT theater_uuid FROM theater WHERE theater_id = %s)
        """, (selectTheaterId,))
        cinemas = cursor.fetchall()

        if not cinemas:
            print("\nNo cinemas available for the selected Theater ID.")
            return
        
        cinema_headers = ["Cinema ID", "Cinema Name", "Duration (mins)", "Cost (INR)"]
        print(tabulate(cinemas, headers=cinema_headers, tablefmt='fancy_grid'))

        selectCinemaId = input("\nEnter the Cinema ID to view show schedule: ")

        cursor.execute("""SELECT s.show_id, t.theater_name, c.cinema_name, s.show_time, s.screen_number, s.schedule_status 
                          FROM shows s 
                          JOIN theater t ON s.theater_uuid = t.theater_uuid 
                          JOIN cinema c ON s.cinema_uuid = c.cinema_uuid 
                          WHERE t.theater_id = %s AND c.cinema_id = %s 
                          ORDER BY s.show_time""", (selectTheaterId, selectCinemaId))
        shows = cursor.fetchall()

        if shows:
            show_headers = ["Show ID", "Theater Name", "Cinema Name", "Show Time", "Screen Number", "Status"]
            print("\nScheduled Shows for the selected cinema:")
            print(tabulate(shows, headers=show_headers, tablefmt='fancy_grid'))

            selectShowId = input("\nEnter the Show ID to be Selected: ")

            cursor.execute("""
                SELECT s.show_id, s.screen_number, s.show_time, t.theater_name, c.cinema_name, s.theater_uuid, 
                       s.cinema_uuid, c.cinema_cost, t.theater_rows, t.theater_columns
                FROM shows s
                JOIN theater t ON s.theater_uuid = t.theater_uuid
                JOIN cinema c ON s.cinema_uuid = c.cinema_uuid
                WHERE s.show_id = %s
            """, (selectShowId,))
            selectedShow = cursor.fetchone()

            if selectedShow:
                print(f"\nSelected Show ID: {selectShowId} Details:")
                show_id, screen_number, show_time, theater_name, cinema_name, theater_uuid, cinema_uuid, cinema_cost, theater_rows, theater_columns = selectedShow
                selectedShowData = [[show_id, screen_number, show_time, theater_name, cinema_name]]
                print(tabulate(selectedShowData, headers=["Show ID", "Screen Number", "Show Time", "Theater Name", "Cinema Name"], tablefmt='fancy_grid'))

                # Seat Layout Display
                cursor.execute("""SELECT seat_row, seat_col FROM booked_seats WHERE show_id = %s""", (selectShowId,))
                booked_seats = cursor.fetchall()

                print("\nAvailable Seats Layout (Use [row,column] to select seats):")
                print("    ", end="")
                for col in range(1, theater_columns + 1):
                    print(f" {col:2}", end=" ")
                print()

                for row in range(1, theater_rows + 1):
                    print(f"{row:2} ", end="")
                    for col in range(1, theater_columns + 1):
                        if (row, col) in [(r[0], r[1]) for r in booked_seats]:
                            print("[X]", end=" ")
                        else:
                            print("[ ]", end=" ")
                    print()

                print("\nTo book seats, enter the format 'row,column' (e.g., 1,2) or 'done' to finish.")
                booked_seats_input = []
                total_price = 0  # Initialize total price

                while True:
                    seat = input("Enter Seat to Book or 'done' to finish: ")
                    if seat.lower() == 'done':
                        break
                    try:
                        row, col = map(int, seat.split(','))
                        if (row, col) in [(r[0], r[1]) for r in booked_seats]:
                            print("This seat is already booked. Please choose another one.")
                        else:
                            booked_seats_input.append((row, col))
                            total_price += cinema_cost  # Dynamically add price based on the selected cinema's cost
                    except ValueError:
                        print("Invalid input format. Please use 'row,column'.")

                # Generate the ticket after booking seats
                ticket_id = str(uuid.uuid4())[:8]
                
                ticket_file = f"cinemahub_ticket_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
                generate_ticket(show_details={
                    "cinema_name": cinema_name,
                    "theater_name": theater_name,
                    "show_time": show_time,
                    "screen_number": screen_number,
                    "ticket_id": ticket_id 
                }, selected_seats=booked_seats_input, total_price=total_price)

                # Insert booked seats into the database
                for seat in booked_seats_input:
                    row, col = seat
                    cursor.execute("""
                        INSERT INTO booked_seats (show_id, theater_uuid, cinema_uuid, seat_row, seat_col, is_booked,ticket_id)
                        VALUES (%s, %s, %s, %s, %s, 'yes',%s)
                    """, (show_id, theater_uuid, cinema_uuid, row, col,ticket_id))  
                    conn.commit()

                # Show confirmation of booking
                print(f"\nYou have booked the following seats:")
                booked_seat_details = [[f"Row {seat[0]}", f"Col {seat[1]}"] for seat in booked_seats_input]
                print(tabulate(booked_seat_details, headers=["Row", "Column"], tablefmt="fancy_grid"))

                print(f"\nTotal Price for booking {len(booked_seats_input)} seat(s): ₹{total_price}")

                print("\nUpdated Available Seats Layout:")
                print("    ", end="")
                for col in range(1, theater_columns + 1):
                    print(f" {col:2}", end=" ")
                print()

                for row in range(1, theater_rows + 1):
                    print(f"{row:2} ", end="")
                    for col in range(1, theater_columns + 1):
                        if (row, col) in [(r[0], r[1]) for r in booked_seats_input]:
                            print("[X]", end=" ")
                        else:
                            print("[ ]", end=" ")
                    print()
            else:
                print("\nInvalid Show ID selected.")
        else:
            print("\nNo schedule details found for the selected Cinema.")

        while True:
            returnGuest = input("\nEnter (y) To Return to Landing Menu (n) To Exit [y/n]: ")
            if returnGuest == 'y':
                welcome_cinemahub()
                break  
            elif returnGuest == 'n':
                print("Thanks For Visiting CineHub....")
                break  
            else:
                print("Invalid input. Please enter 'y' to return to the Admin Menu or 'n' to Exit.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn:
            conn.close()




def generate_ticket(show_details, selected_seats, total_price, background_pdf="C:\\Users\\sbcod\\Downloads\\CinehubTicket.pdf"):
    try:
        # Initialize the ticket_file variable before use
        ticket_file = None

        pdfmetrics.registerFont(TTFont('RobotoMono-Bold', 'C:\\Users\\sbcod\\Desktop\\NEW\\Fonts\\Roboto_Mono\\static\\RobotoMono-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('Acme-Regular', 'C:\\Users\\sbcod\\Desktop\\NEW\\Fonts\\Acme\\Acme-Regular.ttf'))

        # Validate the background PDF file path
        if not os.path.exists(background_pdf):
            raise FileNotFoundError(f"Background PDF not found: {background_pdf}")

        # Read the existing ticket template PDF
        reader = PdfReader(background_pdf)
        writer = PdfWriter()

        # Create a memory buffer for the text overlay
        packet = BytesIO()

        # Create a canvas to draw the text overlay
        can = canvas.Canvas(packet, pagesize=(595.27, 841.89))  # Default A4 size (adjust as needed)
        
        # Set a larger font size for the heading
        can.setFont("Acme-Regular", 22)

        # Add heading text (e.g., CineHub) at the top of the ticket
        heading_x_offset = 102  # Horizontal position of the heading
        heading_y_offset = 483 # Vertical position of the heading (near the top of the page)
        can.drawString(heading_x_offset, heading_y_offset, "C I N E M A H U B")

        # Set font for the rest of the ticket details
        can.setFont("RobotoMono-Bold", 12)

        # Adjust text positions for the other ticket details
        x_offset = 102  # Move text 1.5 inches to the right (108 points)
        y_offset = 460  # Adjust based on your template layout
        line_height = 24  # Space between lines for better readability

        # Add movie and theater details
        can.drawString(x_offset, y_offset, f"Cinema : {show_details['cinema_name']}")
        can.drawString(x_offset, y_offset - line_height, f"Theater : {show_details['theater_name']}")
        can.drawString(x_offset, y_offset - 2 * line_height, f"Show Time : {show_details['show_time']}")
        can.drawString(x_offset, y_offset - 3 * line_height, f"Screen : {show_details['screen_number']}")
        

        # Display ticket_id vertically
        ticket_id = show_details['ticket_id']
        vertical_x_offset = x_offset + 369  # Adjust horizontal position for the vertical text
        vertical_y_offset = y_offset   # Base vertical position
        vertical_line_spacing = 15  # Space between characters

        # Draw each character of the ticket_id vertically
        for i, char in enumerate(ticket_id):
            can.drawString(vertical_x_offset, vertical_y_offset - i * vertical_line_spacing, char)
        

        # Add seat details
        if selected_seats:
            seat_text = f"Seats: {', '.join([f'R{seat[0]}C{seat[1]}' for seat in selected_seats])}"
        else:
            seat_text = "Seats: N/A"
        can.drawString(x_offset, y_offset - 4 * line_height, seat_text)

        # Add total price
        can.drawString(x_offset, y_offset - 5 * line_height, f"Total Price: Rs:{total_price}")

        # Add a footer message
        can.setFont("Helvetica-Oblique", 10)  # Smaller font for footer
        can.drawString(x_offset, y_offset - 8 * line_height, "Thank you for booking with CineHub!")

        # Finalize the overlay
        can.save()
        packet.seek(0)

        # Read the overlay PDF
        overlay = PdfReader(packet)

        # Merge overlay onto each page of the background PDF
        for page in reader.pages:
            page.merge_page(overlay.pages[0])  # Overlay the text onto the first page
            writer.add_page(page)

        # Generate the ticket file name with datetime
        c_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        ticket_file = f"C:\\Users\\sbcod\\Desktop\\cinemahub_ticket_{c_datetime}.pdf"

        # Save the final ticket with merged content
        with open(ticket_file, "wb") as output_file:
            writer.write(output_file)

        print(f"Ticket successfully saved as: {ticket_file}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")





    
#VIEW BOOKED SEATS
def viewBookings():
    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        print("\nHere are the list of all Theaters:\n")
        cursor.execute("SELECT theater_id, theater_name FROM theater")
        theaters = cursor.fetchall()

        if not theaters:
            print("No theaters available.")
            return
        
        theater_headers = ["Theater ID", "Theater Name"]
        print(tabulate(theaters, headers=theater_headers, tablefmt='fancy_grid'))

        selectTheaterId = input("\nEnter the Theater ID to view cinemas: ")

       
        cursor.execute("""
            SELECT cinema_id, cinema_name
            FROM cinema
            WHERE cinema_theater_uuid = (SELECT theater_uuid FROM theater WHERE theater_id = %s)
        """, (selectTheaterId,))
        cinemas = cursor.fetchall()

        if not cinemas:
            print("\nNo cinemas available for the selected Theater ID.")
            return
        
        cinema_headers = ["Cinema ID", "Cinema Name"]
        print(tabulate(cinemas, headers=cinema_headers, tablefmt='fancy_grid'))

        selectCinemaId = input("\nEnter the Cinema ID to view show schedule: ")

       
        cursor.execute("""
            SELECT s.show_id, c.cinema_name, s.show_time 
            FROM shows s
            JOIN cinema c ON s.cinema_uuid = c.cinema_uuid
            WHERE c.cinema_id = %s
        """, (selectCinemaId,))
        shows = cursor.fetchall()

        if not shows:
            print("\nNo shows available for the selected Cinema ID.")
            return
        
        show_headers = ["Show ID", "Cinema Name", "Show Time"]
        print(tabulate(shows, headers=show_headers, tablefmt='fancy_grid'))

        selectShowId = input("\nEnter the Show ID to view seat availability: ")

        
        cursor.execute("""
            SELECT s.show_id, t.theater_rows, t.theater_columns
            FROM shows s
            JOIN theater t ON s.theater_uuid = t.theater_uuid
            WHERE s.show_id = %s
        """, (selectShowId,))
        show_details = cursor.fetchone()

        if not show_details:
            print("\nInvalid Show ID selected.")
            return

        show_id, theater_rows, theater_columns = show_details

        
        cursor.execute("""
            SELECT seat_row, seat_col
            FROM booked_seats
            WHERE show_id = %s
        """, (selectShowId,))
        booked_seats = cursor.fetchall()

        
        print("\nBooked Seats:")
        print("    ", end="")
        for col in range(1, theater_columns + 1):
            print(f" {col:2}", end=" ") 
        print() 

        for row in range(1, theater_rows + 1):
            print(f"{row:2} ", end="") 
            for col in range(1, theater_columns + 1):
                if (row, col) in [(r[0], r[1]) for r in booked_seats]:
                    print("[X]", end=" ")  
                else:
                    print("[]", end=" ")  
            print()  

        
        while True:
            returnGuest = input("\nEnter (y) To Return to Main Menu or (n) To Exit [y/n]: ")
            if returnGuest.lower() == 'y':
                welcome_cinemahub()  
                break  
            elif returnGuest.lower() == 'n':
                print("Thanks For Visiting CineHub....")
                break  
            else:
                print("Invalid input. Please enter 'y' to return to the main menu or 'n' to exit.")
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn:
            conn.close()

#Booking Cancelation
def admin_cancelBooking():
    try:
        conn = mysql.connector.connect(**db_connection)
        cursor = conn.cursor()

        # Display all booked seats for all users
        print("\nAll Booked Seats (Use Booking ID to Cancel):")
        cursor.execute("""
            SELECT b.booking_id, b.show_id, b.seat_row, b.seat_col, b.username, c.cinema_name
            FROM booked_seats b
            JOIN cinema c ON b.cinema_uuid = c.cinema_uuid
            WHERE b.is_booked = 'yes'
        """)
        booked_seats = cursor.fetchall()

        if not booked_seats:
            print("No booked seats available.")
            return
        
        booked_seats_headers = ["Booking ID", "Show ID", "Row", "Column", "Username", "Cinema Name"]
        print(tabulate(booked_seats, headers=booked_seats_headers, tablefmt="fancy_grid"))

        # Get the Booking ID from the admin for cancellation
        booking_id_to_cancel = input("\nEnter the Booking ID to Cancel: ")

        # Check if the Booking ID exists and is currently booked
        cursor.execute("""
            SELECT booking_id 
            FROM booked_seats 
            WHERE booking_id = %s AND is_booked = 'yes'
        """, (booking_id_to_cancel,))
        booking = cursor.fetchone()

        if not booking:
            print("Invalid Booking ID or the seat is not currently booked.")
            return

        # Cancel the booking (update is_booked to 'no')
        cursor.execute("""
            UPDATE booked_seats 
            SET is_booked = 'no' 
            WHERE booking_id = %s
        """, (booking_id_to_cancel,))
        conn.commit()

        print(f"Booking with ID {booking_id_to_cancel} has been successfully canceled.")

        # Display updated list of all booked seats
        print("\nUpdated Booked Seats:")
        cursor.execute("""
            SELECT b.booking_id, b.show_id, b.seat_row, b.seat_col, b.username, c.cinema_name
            FROM booked_seats b
            JOIN cinema c ON b.cinema_uuid = c.cinema_uuid
            WHERE b.is_booked = 'yes'
        """)
        updated_booked_seats = cursor.fetchall()

        if updated_booked_seats:
            print(tabulate(updated_booked_seats, headers=booked_seats_headers, tablefmt="fancy_grid"))
        else:
            print("No remaining booked seats.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn:
            conn.close()



# Calling Display Banner
display_cinema_hub()

while True:
    choice = welcome_cinemahub()  # Get the user's choice

    if choice == 1:
        signupUser()
    elif choice == 2:
        loginpage()
    elif choice == 3:
        print("Browsing As a Guest...")
        # Modify browse to return a signal when exiting
        should_exit = browse()
        if should_exit is False:  # Check if user chose to exit from `browse()`
            print("Thanks for visiting CineHub. Goodbye!")
            break
    elif choice == 4:
        print("You exited the Landing Menu.")
        break
    else:
        print("Invalid choice. Please try again.")

# Generate ticket if needed (depends on logic in your program)
generate_ticket(selected_seats, total_price, background_pdf, output_pdf)



