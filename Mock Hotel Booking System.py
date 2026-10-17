from appjar import gui #Import the appJar GUI library for building the interface
app = gui("CalorHotels") #Create the main application window titled "CalorHotels"
app.setSize("FullScreen") #Set the main window to fill the entire screen
app.setFont(family = "Britannic Bold") #Set the default font for the application
import sqlite3 #Import the library to operate SQLite databases
con = sqlite3.connect("HotelDatabase.db") #Connect to the hotel SQLite database file
con.execute("PRAGMA foreign_keys = ON") #Enable foreign key constraint enforcement in SQLite
cur = con.cursor() #Create a cursor object to execute SQL queries
import random #Import random for OTP generation
import smtplib #Import smtplib to send emails via SMTP
from email.message import EmailMessage #Import EmailMessage to construct email objects
SenderEmail = "ENTER EMAIL HERE" #The Gmail address used to send system emails
SenderPassword = "ENTER APP PASSWORD HERE" #App password for the sender Gmail account
ForgottenPasswordOTP = None #Global variable to store the current OTP
import re #Import re for regular expression validation
import datetime #Import datetime for date comparisons and date picker handling

#Global variables to track the user's current booking session state
SelectedRoomID = None #Stores the RoomID of the room the guest has selected
SelectedRoomType = None #Stores the room type name of the selected room
SelectedHotelID = None #Stores the HotelID of the hotel branch being booked
BookingGuestCount = None #Number of guests for the current booking
BookingLocation = None #Branch location chosen for the current booking
BookingArrivalDate = None #Chosen arrival date for the current booking
BookingDepartureDate = None #Chosen departure date for the current booking
CurrentGuestID = None #GuestID of the currently logged-in guest
SelectedGuestID = None #GuestID of the guest selected by staff in the guest table
SelectedBookingID = None #BookingID of the booking selected by staff in the booking table

### LOGIN VALIDATION FUNCTION ###
def LoginDetailsValidation():
    global CurrentGuestID #Allow this function to update the global variable guest ID
    LoginEmailEntry = app.getEntry("Email Address:") #Retrieve the email typed into the login form
    LoginPasswordEntry = app.getEntry("Password:") #Retrieve the password typed into the login form
    if LoginEmailEntry == "" or LoginPasswordEntry == "": #Check that neither field is empty
        app.infoBox("EmptyDetailsError", "Please enter both email and password")
        return False
    cur.execute("SELECT GuestID, Password FROM tbl_guests WHERE EmailAddress = ?",(LoginEmailEntry,)) #Query the database for a guest with the entered email
    result = cur.fetchone() #Fetch the first matching record
    if result is None: #If no record found, the email is not registered
        app.infoBox("InvalidEmailError", "Email does not exist")
        return False
    if LoginPasswordEntry != result[1]: #Compare entered password against the stored password
        app.infoBox("InvalidPasswordError", "Password incorrect")
        return False
    CurrentGuestID = result[0] #Store the logged-in guest's ID for use throughout the session
    return True
### END LOGIN VALIDATION FUNCTION ###

### STAFF LOGIN VALIDATION FUNCTION ###
def StaffLoginDetailsValidation():
    StaffLoginEmailEntry = app.getEntry("Enter Your Staff Email Address:") #Retrieve the email from the staff login form
    StaffLoginPasswordEntry = app.getEntry("Enter Your Staff Password:") #Retrieve the password from the staff login form
    cur.execute("SELECT EmailAddress, Password FROM tbl_staff WHERE EmailAddress = ?",(StaffLoginEmailEntry,)) #Query staff table for the entered email
    result = cur.fetchone() #Fetch the matching staff record if it exists
    if result is None: #If no staff record found, the email is not registered as staff
        app.infoBox("InvalidEmailError", "Email does not exist")
        return False
    elif StaffLoginPasswordEntry != result[1]: #Compare entered password with the stored staff password
        app.infoBox("InvalidPasswordError", "Password incorrect")
        return False
    return True
### END STAFF LOGIN VALIDATION FUNCTION ###

### SIGN UP APPEND FUNCTION ###
def SignUpDetailsAppend():
    SignUpFirstNameEntry = app.getEntry("First Name:") #Retrieve the entered first name
    SignUpLastNameEntry = app.getEntry("Last Name:") #Retrieve the entered last name
    SignUpEmailAddressEntry = app.getEntry("Email Address") #Retrieve the entered email address
    SignUpPasswordEntry = app.getEntry("Password") #Retrieve the entered password
    SignUpPasswordReEntry = app.getEntry("Re-type Password:") #Retrieve the re-typed password for confirmation
    SignUpPhoneNumberEntry = app.getEntry("Phone Number") #Retrieve the entered phone number
    if not all([SignUpFirstNameEntry, SignUpLastNameEntry, SignUpEmailAddressEntry, SignUpPasswordEntry, SignUpPasswordReEntry, SignUpPhoneNumberEntry]): #Check all fields are not empty, 'all' returns False if any value is empty
        app.infoBox("MissingDataError", "Error: All fields must be filled in")
        return False
    if not SignUpFirstNameEntry.isalpha() or not SignUpLastNameEntry.isalpha(): #Ensure names contain only alphabetic characters (no digits or symbols)
        app.infoBox("InvalidNameError", "Error: Names can only contain letters")
        return False
    if len(SignUpFirstNameEntry) > 25 or len(SignUpLastNameEntry) > 25: #Enforce a maximum name length of 25 characters
        app.infoBox("NameLengthError", "Error: Names must be 25 characters or less")
        return False
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$" #Regex pattern to validate a standard email format
    if not re.match(email_pattern, SignUpEmailAddressEntry): #Check the email matches the expected format
        app.infoBox("InvalidEmailError", "Error: Please enter a valid email address")
        return False
    special_characters = "!@#$%^&*()-_=+[]{}|;':,.<>/?~\"" #String of accepted special characters for passwords
    if len(SignUpPasswordEntry) < 8: #Enforce minimum password length of 8 characters
        app.infoBox("PasswordLengthError", "Error: Password must be at least 8 characters long")
        return False
    if not any(char.isupper() for char in SignUpPasswordEntry): #Check at least one uppercase letter is present
        app.infoBox("PasswordUppercaseError", "Error: Password must contain at least one uppercase letter")
        return False
    if not any(char.islower() for char in SignUpPasswordEntry): #Check at least one lowercase letter is present
        app.infoBox("PasswordLowercaseError", "Error: Password must contain at least one lowercase letter")
        return False
    if not any(char.isdigit() for char in SignUpPasswordEntry): #Check at least one digit is present
        app.infoBox("PasswordDigitError", "Error: Password must contain at least one digit")
        return False
    if not any(char in special_characters for char in SignUpPasswordEntry): #Check at least one special character is present
        app.infoBox("PasswordSpecialCharError", "Error: Password must contain at least one special character")
        return False
    if SignUpPasswordEntry != SignUpPasswordReEntry: #Ensure both password fields match
        app.infoBox("PasswordMismatchError", "Error: Passwords do not match")
        return False
    if not SignUpPhoneNumberEntry.isdigit(): #Ensure phone number contains only numeric digits
        app.infoBox("PhoneNumberError", "Error: Phone number must contain only digits")
        return False
    if len(SignUpPhoneNumberEntry) != 11: #Enforce exactly 11 digits for a UK phone number
        app.infoBox("PhoneNumberLengthError", "Error: Phone number must be 11 digits")
        return False
    cur.execute("SELECT EmailAddress FROM tbl_guests WHERE EmailAddress = ?", (SignUpEmailAddressEntry,)) #Check if this email is already registered
    if cur.fetchone() is not None: #If a record exists, this email is already taken
        app.infoBox("ExistingEmailError", "Error: Email address already registered")
        return False
    try:
        cur.execute("""INSERT INTO tbl_guests (FirstName, LastName, EmailAddress, Password, PhoneNumber) VALUES (?, ?, ?, ?, ?)""",(SignUpFirstNameEntry, SignUpLastNameEntry, SignUpEmailAddressEntry, SignUpPasswordEntry, SignUpPhoneNumberEntry)) #Insert the new guest record into the database with all provided details
        con.commit() #Commits the changes so the insert is saved permanently
        app.infoBox("SuccessfulSignUp", "Successfully signed up!")
        return True
    except sqlite3.IntegrityError: #Catch any database constraint violations (e.g. duplicate unique fields)
        app.infoBox("DatabaseError", "Error: Could not insert into database")
        return False
### END SIGN UP APPEND FUNCTION ###

### FORGOTTEN PASSWORD FUNCTIONS ###
def ForgottenPasswordValidation():
    ForgottenPasswordEmailEntry = app.getEntry("Please Enter Your Email Address:") #Retrieve the entered email address
    cur.execute("SELECT EmailAddress FROM tbl_guests WHERE EmailAddress = ?", [ForgottenPasswordEmailEntry]) #Query DB to check if email exists
    result = cur.fetchone() #Fetch the matching guest email record
    if result is None: #If no record found, the email is not registered
        app.infoBox("NonExistantEmailError", "Error, Entered Email Address Does Not Exist")
        return False
    else:
        return True

def SendForgottenOTP():
    global ForgottenPasswordOTP #Allow this function to set the global OTP variable
    SelectedEmailAddress = app.getEntry("Please Enter Your Email Address:") #Retrieve the email to send the OTP to
    cur.execute("SELECT EmailAddress FROM tbl_guests") #Fetch all registered guest email addresses
    DatabaseEmails = [row[0] for row in cur.fetchall()] #Build a list of all email addresses from the results
    if SelectedEmailAddress not in DatabaseEmails: #Verify the entered email exists in the database
        app.infoBox("NonExistantEmailError", "Error, Entered Email Address Does Not Exist")
        return
    ForgottenPasswordOTP = random.randint(100000, 999999) #Generate a random 6-digit OTP
    msg = EmailMessage() #Create a new email message object
    msg["From"] = SenderEmail #Set the sender address
    msg["To"] = SelectedEmailAddress #Set the recipient to the guest's email
    msg["Subject"] = "Your OTP" #Set the email subject line
    msg.set_content(f"Your OTP is: {ForgottenPasswordOTP}") #Set the body with the generated OTP
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp: #Connect to Gmail's SMTP server on port 587
        smtp.starttls() #Upgrade the connection to encrypted TLS
        smtp.login(SenderEmail, SenderPassword) #Authenticate with the sender's credentials
        smtp.send_message(msg) #Send the constructed email message
    app.infoBox("OTPSent", f"An OTP has been sent to {SelectedEmailAddress}")

def ResendForgottenOTP():
    global ForgottenPasswordOTP #Allow this function to regenerate the global OTP if needed
    SelectedEmailAddress = app.getEntry("Please Enter Your Email Address:") #Retrieve the email to resend to
    if ForgottenPasswordOTP is None: #If no OTP exists yet, generate one before resending
        ForgottenPasswordOTP = random.randint(100000, 999999)
    msg = EmailMessage() #Create a new email message object for the resend
    msg["From"] = SenderEmail
    msg["To"] = SelectedEmailAddress
    msg["Subject"] = "Your OTP (Resent)" #Label the subject to indicate this is a resent OTP
    msg.set_content(f"Your OTP is: {ForgottenPasswordOTP}") #Include the same OTP in the body
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(SenderEmail, SenderPassword)
        smtp.send_message(msg)
    app.infoBox("ConfirmResend", "OTP Has Been Resent")

def ValidateForgottenOTP():
    global ForgottenPasswordOTP #Access the globally stored OTP for comparison
    EnteredOTP = app.getEntry("OTP_Entry") #Retrieve the OTP string typed by the user
    if str(ForgottenPasswordOTP) == EnteredOTP: #Compare entered OTP as a string to the stored integer OTP
        return True
    else:
        app.infoBox("IncorrectOTP", "Error, Entered OTP Does Not Match System OTP")
### END FORGOTTEN PASSWORD FUNCTIONS ###

### CHANGE PASSWORD FUNCTION ###
def ChangePasswordValidation():
    DesiredEmail = app.getEntry("Please Enter Your Email Address:") #Retrieve the email entered in the forgot password screen
    ChangePassword = app.getEntry("Please Enter Your New Password:") #Retrieve the desired new password
    ReEntryChangePassword = app.getEntry("Please Re-Enter Your Password:") #Retrieve the re-typed new password
    cur.execute("SELECT Password FROM tbl_guests WHERE EmailAddress = ?", (DesiredEmail,)) #Query the database for the current password of the entered email
    CurrentPassword = cur.fetchone() #Fetch the current password record
    SpecialCharacters = "!@#$%^&*()-_=+[]{}|;':,.<>/?~\"" #Accepted special characters for password validation
    if ChangePassword == ReEntryChangePassword: #Ensure both password entries match before proceeding
        if CurrentPassword[0] != ChangePassword:
            if len(ChangePassword) >= 8 and any(char in SpecialCharacters for char in ChangePassword) and any(char.isdigit() for char in ChangePassword) and any(char.isupper() for char in ChangePassword): #Validate the password meets all requirements
                cur.execute("UPDATE tbl_guests SET Password = ? WHERE EmailAddress = ?",(ChangePassword, DesiredEmail)) #Update the guest's password in the database
                con.commit() #Commits the update so it is permanently saved
                return True
            else:
                app.infoBox("PasswordRequirements", "Error, Password must be at least 8 characters, includes a special character, includes a digit and includes an uppercase letter")
                return False
        else:
            app.infoBox("SamePasswordError", "Error, New password cannot be the same as the old password")
            return False
    else:
        app.infoBox("PasswordNotMatchError", "Error, Passwords Do Not Match")
        return False
### END CHANGE PASSWORD FUNCTION ###

### STAFF DISPLAY FUNCTIONS ###
def StaffLoadGuestTable():
    cur.execute("SELECT GuestID, FirstName, LastName, EmailAddress, Password, PhoneNumber FROM tbl_guests") #Fetch all guest records from the database
    rows = cur.fetchall() # Retrieve all rows from the query result
    TableData = [["ID", "First Name", "Last Name", "Email", "Password", "Phone Number"]] #Initialise table data with a header row
    for i in rows:
        TableData.append(list(i)) #Convert each database row tuple to a list and append to table data
    try:
        app.deleteAllTableRows("GuestTable") #Attempt to clear existing rows before repopulating
    except:
        pass #Ignore any errors if the table has no rows to delete yet
    app.replaceAllTableRows("GuestTable", TableData) #Populate the guest table widget with the fresh data

def GuestAction(btn):
    global SelectedGuestID #Allow this function to update the global variable selected guest
    SelectedButton = app.getTableSelectedCells("GuestTable") #Retrieve the currently selected cell(s) in the guest table
    if not SelectedButton: #If no cell is selected, prompt the user to make a selection
        app.infoBox("NotSelectedBooking", "Error, Please Select A Guest")
        return
    selected_row = int(SelectedButton[0].split("-")[0])
    row_data = app.getTableRow("GuestTable", selected_row)#Retrieve all data from the selected row
    SelectedGuestID = row_data[0] #Store the GuestID from the selected row
    app.hideSubWindow("win_staffguests")
    app.showSubWindow("win_guestaction")

def StaffDisplayGuestTable():
    StaffLoadGuestTable() #Reloads the table data whenever the guest display is shown

def StaffLoadBookingTable():
    cur.execute("SELECT BookingID, GuestID, HotelID, RoomID, GuestCount, ArrivalDate, DepartureDate FROM tbl_bookings") #Fetch all booking records from the database
    rows = cur.fetchall() #Retrieve all booking rows from the query
    TableData = [["Booking ID", "Guest ID", "Hotel ID", "Room ID", "Guest Count", "Arrival Date", "Departure Date"]] #Initialise table data with a header row
    for i in rows:
        TableData.append(list(i)) #Convert each booking row tuple to a list and append
    try:
        app.deleteAllTableRows("BookingTable") #Attempt to clear existing rows before repopulating
    except:
        pass #Ignore errors if the table is already empty
    app.replaceAllTableRows("BookingTable", TableData) #Populate the booking table widget with fresh data

def BookingAction(btn):
    global SelectedBookingID #Allow this function to update the globally tracked selected booking
    SelectedCells = app.getTableSelectedCells("BookingTable") #Retrieve the currently selected cells in the booking table
    if not SelectedCells: #If no cell is selected, prompt the user to make a selection
        app.infoBox("NotSelectedBooking", "Error, Please Select A Booking")
        return
    selected_row = int(SelectedCells[0].split("-")[0])
    row_data = app.getTableRow("BookingTable", selected_row) #Retrieve all data from the selected row
    SelectedBookingID = row_data[0] #Store the BookingID from the selected row
    app.hideSubWindow("win_bookingtable")
    app.showSubWindow("win_bookingaction")

def LoadBookingEdit():
    cur.execute("SELECT GuestCount, ArrivalDate, DepartureDate, RoomID FROM tbl_bookings WHERE BookingID = ?", (SelectedBookingID,)) #Fetch the current booking details for the selected booking
    booking_info = cur.fetchone() #Retrieve the single booking record
    cur.execute("SELECT tbl_roomtype.TypeName, tbl_branch.Location FROM tbl_rooms JOIN tbl_roomtype ON tbl_rooms.TypeID = tbl_roomtype.TypeID JOIN tbl_branch ON tbl_rooms.HotelID = tbl_branch.HotelID WHERE tbl_rooms.RoomID = ?", (booking_info[3],)) #Join rooms, room types, and branch tables to get the room type name and hotel location for this booking
    room_info = cur.fetchone() #Retrieve the room type and location data
    app.setOptionBox("Edit Guest Count", str(booking_info[0])) #Preset guest count with the current booking value
    app.setOptionBox("Edit Location:", room_info[1]) #Preset location with the current branch location
    app.setDatePicker("Edit Arrival Date",  datetime.datetime.strptime(booking_info[1], "%Y-%m-%d")) #Preset arrival date picker, converting the stored string date to a datetime object
    app.setDatePicker("Edit Departure Date", datetime.datetime.strptime(booking_info[2], "%Y-%m-%d")) #Preset departure date picker similarly
    app.setOptionBox("Edit Room Type", room_info[0]) #Preset room type with the current room type name

def EditBookingAppend():
    EditGuestCount = int(app.getOptionBox("Edit Guest Count")) #Get the selected guest count as an integer
    EditArrivalDate = app.getDatePicker("Edit Arrival Date") #Get the selected arrival date
    EditDepartureDate = app.getDatePicker("Edit Departure Date") #Get the selected departure date
    EditRoomType = app.getOptionBox("Edit Room Type") #Get the selected room type name
    EditLocation = app.getOptionBox("Edit Location:") #Get the selected branch location name
    CurrentArrival = EditArrivalDate
    CurrentDeparture = EditDepartureDate
    if CurrentDeparture <= CurrentArrival: #Validate that departure is after arrival
        app.infoBox("DateOverlapError", "Departure date must be after arrival date")
        return False
    cur.execute("SELECT HotelID FROM tbl_branch WHERE Location = ?", (EditLocation,)) #Look up the HotelID for the chosen location
    hotel = cur.fetchone()
    if not hotel: #If no hotel found for this location, show an error
        app.infoBox("NonExistantLocationError", "Location does not exist")
        return False
    HotelID = hotel[0] #Extract the HotelID from the query result
    cur.execute("SELECT tbl_rooms.RoomID FROM tbl_rooms JOIN tbl_roomtype ON tbl_rooms.TypeID = tbl_roomtype.TypeID WHERE tbl_rooms.HotelID = ? AND tbl_roomtype.Capacity >= ? AND tbl_rooms.RoomID NOT IN (SELECT tbl_bookings.RoomID FROM tbl_bookings WHERE NOT (tbl_bookings.DepartureDate <= ? OR tbl_bookings.ArrivalDate >= ?))", (HotelID, EditGuestCount, EditArrivalDate, EditDepartureDate)) #Find an available room at the chosen hotel with sufficient capacity that is not already booked for the selected dates
    room = cur.fetchone()
    if not room: #If no available room found, inform the user
        app.infoBox("NoRoomError", "No available rooms matching criteria")
        return False
    NewRoomID = room[0] #Extract the RoomID of the newly assigned available room
    cur.execute("SELECT RoomID FROM tbl_bookings WHERE BookingID = ?", (SelectedBookingID,)) #Retrieve the old RoomID
    OldRoomID = cur.fetchone()[0]
    cur.execute("UPDATE tbl_bookings SET GuestCount = ?, ArrivalDate = ?, DepartureDate = ?, HotelID = ?, RoomID = ? WHERE BookingID = ?",(EditGuestCount, EditArrivalDate, EditDepartureDate, HotelID, NewRoomID, SelectedBookingID)) #Update the booking record with all new values for this booking ID
    con.commit() #Commit the update to save changes
    app.infoBox("EditSuccess", "Booking Successfully Updated")
    return True
### END STAFF DISPLAY FUNCTIONS ###

def SetCurrentDate():
    app.setDatePicker("Date Of Arrival", datetime.datetime.now()) #Set the arrival date picker to today's date
    app.setDatePicker("Date Of Departure", datetime.datetime.now()) #Set the departure date picker to today's date

def MainMenuCriteria():
    MainMenuLocationEntry = app.getOptionBox("Enter Branch Location") #Get the branch location chosen by the guest
    MainMenuRoomTypeEntry = app.getOptionBox("Room Type") #Get the room type chosen by the guest
    MainMenuGuestCountEntry = int(app.getOptionBox("Guest Count")) #Get the guest count as an integer
    MainMenuArrivalDate = app.getDatePicker("Date Of Arrival") #Get the chosen arrival date
    MainMenuDepartureDate = app.getDatePicker("Date Of Departure") #Get the chosen departure date
    if MainMenuDepartureDate <= MainMenuArrivalDate: #Validate departure is after arrival
        app.infoBox("DateError", "Departure date must be after arrival date")
        return False
    cur.execute("SELECT HotelID FROM tbl_branch WHERE Location = ?",(MainMenuLocationEntry,)) #Look up the HotelID for the chosen location
    hotel = cur.fetchone()
    if not hotel: #If no hotel found for this location, inform the user
        app.infoBox("LocationError", "Location does not exist")
        return False
    HotelID = hotel[0] #Extract the HotelID
    cur.execute("SELECT tbl_rooms.RoomID FROM tbl_rooms JOIN tbl_roomtype ON tbl_rooms.TypeID = tbl_roomtype.TypeID WHERE tbl_rooms.HotelID = ? AND tbl_roomtype.TypeName = ? AND tbl_roomtype.Capacity >= ? AND tbl_rooms.RoomID NOT IN (SELECT tbl_bookings.RoomID FROM tbl_bookings WHERE NOT (tbl_bookings.DepartureDate <= ? OR tbl_bookings.ArrivalDate >= ?))", (HotelID, MainMenuRoomTypeEntry, MainMenuGuestCountEntry, MainMenuArrivalDate, MainMenuDepartureDate)) #Find all rooms at the selected hotel matching the room type and capacity that are not already booked for the chosen dates
    rooms = cur.fetchall() #Retrieve all matching available room records
    if not rooms: #If no rooms available, inform the guest
        app.infoBox("UnavailableRoomError", "No rooms available")
        return False
    return HotelID, rooms #Return the HotelID and list of available room IDs

def DisplayAvailableRooms(available_rooms):
    global SelectedRoomID
    SelectedRoomID = None #Reset any previously selected room before showing new options
    app.emptySubWindow("win_booking") #Clear all existing widgets from the booking window
    app.openSubWindow("win_booking") #Open the booking subwindow in edit mode to add new widgets
    app.addLabel("BookingTitle", "Booking") #Add a title label to the booking window

    for i, room_id in enumerate(available_rooms, start=1): #Iterate over available rooms, starting from 1
        room_id = room_id[0] #Extract the RoomID integer from the tuple
        button_name = f"Booking_Room_{room_id}" #Create a unique button name using the room ID
        display_name = f"Room {i} (ID: {room_id})" #Create a human readable label showing the room number and ID
        app.addNamedButton(display_name, button_name, makeRoomCallback(room_id)) #Add a button for each available room
        app.setButtonBg(button_name, "#e83d1b")
        app.setButtonFg(button_name, "#1a1a19")
    app.addNamedButton("Return To Main Menu", "Booking_Return", btnpress) #Add a return button below the room list
    app.setButtonBg("Booking_Return", "#e83d1b")
    app.setButtonFg("Booking_Return", "#1a1a19")
    app.stopSubWindow() #Close the subwindow edit context

def makeRoomCallback(room_id):
    #Returns a closure so each room button correctly captures its own room id, Without this, all buttons would reference the same loop variable
    def callback(btn):
        SelectRoom(room_id)
    return callback

def SelectRoom(room_id):
    global SelectedRoomID
    SelectedRoomID = room_id #Store the chosen room ID globally for use during booking confirmation
    LoadBookingSummary() #Populate the booking summary screen with the selected room's details
    app.hideSubWindow("win_booking")
    app.showSubWindow("win_bookingsummary")

def LoadBookingSummary():
    global BookingGuestCount, BookingLocation, BookingArrivalDate, BookingDepartureDate, SelectedRoomType, SelectedHotelID
    BookingGuestCount = int(app.getOptionBox("Guest Count")) #Store the chosen guest count globally
    BookingLocation = app.getOptionBox("Enter Branch Location") #Store the chosen location globally
    BookingArrivalDate = app.getDatePicker("Date Of Arrival") #Store the chosen arrival date globally
    BookingDepartureDate = app.getDatePicker("Date Of Departure") #Store the chosen departure date globally
    CurrentArrival = BookingArrivalDate
    CurrentDeparture = BookingDepartureDate
    if CurrentDeparture <= CurrentArrival: #Validate departure is strictly after arrival
        app.infoBox("DateError", "Departure date must be after arrival date")
        return
    cur.execute("""SELECT tbl_roomtype.TypeName, tbl_rooms.HotelID FROM tbl_rooms JOIN tbl_roomtype ON tbl_rooms.TypeID = tbl_roomtype.TypeID WHERE tbl_rooms.RoomID = ? """, (SelectedRoomID,)) #Retrieve the room type name and hotel ID for the selected room
    room_info = cur.fetchone()
    if room_info is None: #If room details could not be loaded, show an error
        app.infoBox("LoadingRoomError", "Error loading room information")
        return
    SelectedRoomType = room_info[0] #Store the room type name globally
    SelectedHotelID = room_info[1] #Store the hotel ID globally
    app.setLabel("GuestCountSummary", f"Guests: {BookingGuestCount}") #Display guest count on the summary screen
    app.setLabel("LocationSummary", f"Location: {BookingLocation}") #Display location on the summary screen
    app.setLabel("RoomTypeSummary", f"Room: {SelectedRoomType} (ID {SelectedRoomID})") #Display room type and ID
    app.setLabel("ArrivalSummary", f"Arrival: {BookingArrivalDate}") #Display arrival date on the summary screen
    app.setLabel("DepartureSummary", f"Departure: {BookingDepartureDate}") #Display departure date on the summary screen

def ConfirmBooking():
    try:
        cur.execute("INSERT INTO tbl_bookings(ArrivalDate, DepartureDate, GuestCount, HotelID, GuestID, RoomID) VALUES (?, ?, ?, ?, ?, ?)", (BookingArrivalDate,BookingDepartureDate,BookingGuestCount,SelectedHotelID,CurrentGuestID,SelectedRoomID)) #Insert the confirmed booking into the database using all globally stored booking details
        con.commit() #Commit the insert to save the booking
        SendBookingEmail() #Send a confirmation email to the guest
        return True
    except sqlite3.IntegrityError: #Catch any database constraint violations during insert
        app.infoBox("DatabaseError", "Error: Could not insert into database")
        return False

def SendBookingEmail():
    msg = EmailMessage() #Create a new email message object
    msg["Subject"] = "Booking Confirmation"
    msg["From"] = SenderEmail
    cur.execute("SELECT EmailAddress FROM tbl_guests WHERE GuestID = ?", (CurrentGuestID,)) #Look up the guest's email using their GuestID
    email = cur.fetchone()[0] #Extract the email address string from the result
    msg["To"] = email #Set the recipient to the guest's email
    msg.set_content(f"""
    Booking Confirmed

    Room ID: {SelectedRoomID}
    Room Type: {SelectedRoomType}
    Location: {BookingLocation}
    Guests: {BookingGuestCount}
    Arrival: {BookingArrivalDate}
    Departure: {BookingDepartureDate}""") #Set the email body with a full booking summary using f-string
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(SenderEmail, SenderPassword)
        smtp.send_message(msg)

def ReturnToMainMenu(btn):
    app.hideSubWindow("win_bookingsummary") #Hide the booking summary screen
    app.showSubWindow("win_mainmenu") #Return to the main menu
    SetCurrentDate() #Reset date pickers to today's date

def ResetBookingGlobals():
    global SelectedRoomID, SelectedRoomType, SelectedHotelID, BookingGuestCount, BookingLocation, BookingArrivalDate, BookingDepartureDate, SelectedGuestID, SelectedBookingID
    SelectedRoomID = None #Clear the selected room ID
    SelectedRoomType = None #Clear the selected room type
    SelectedHotelID = None #Clear the selected hotel ID
    BookingGuestCount = None #Clear the stored guest count
    BookingLocation = None #Clear the stored location
    BookingArrivalDate = None #Clear the stored arrival date
    BookingDepartureDate = None #Clear the stored departure date
    SelectedGuestID = None #Clear the selected guest ID for staff
    SelectedBookingID = None #Clear the selected booking ID for staff

def LoadGuestEdit():
    cur.execute("SELECT FirstName, LastName, EmailAddress, PhoneNumber FROM tbl_guests WHERE GuestID = ?", (SelectedGuestID,)) #Fetch the current details for the selected guest from the database
    guest_info = cur.fetchone() #Retrieve the single guest record
    app.setEntry("Edit First Name:", guest_info[0]) # Preset the first name field with the current value
    app.setEntry("Edit Last Name:", guest_info[1]) # Preset the last name field with the current value
    app.setEntry("Edit Email Address:", guest_info[2]) # Preset the email field with the current value
    app.setEntry("Edit Phone Number:", guest_info[3]) # Preset the phone number field with the current value

def EditGuestDetailsAppend():
    EditFirstNameEntry = app.getEntry("Edit First Name:") # Retrieve the edited first name
    EditLastNameEntry = app.getEntry("Edit Last Name:") # Retrieve the edited last name
    EditEmailAddressEntry = app.getEntry("Edit Email Address:") # Retrieve the edited email address
    EditPhoneNumberEntry = app.getEntry("Edit Phone Number:") # Retrieve the edited phone number
    if not all([EditFirstNameEntry, EditLastNameEntry, EditEmailAddressEntry, EditPhoneNumberEntry]): #Check all edit fields are not empty
        app.infoBox("MissingDataErrorGuestEdit", "Error: All fields must be filled in")
        return False
    if not EditFirstNameEntry.isalpha() or not EditLastNameEntry.isalpha(): #Ensure names contain only alphabetic characters
        app.infoBox("InvalidNameErrorGuestEdit", "Error: Names can only contain letters")
        return False
    if len(EditFirstNameEntry) > 25 or len(EditLastNameEntry) > 25: #Enforce maximum name length of 25 characters
        app.infoBox("NameLengthErrorGuestEdit", "Error: Names must be 25 characters or less")
        return False
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$" #Regex for standard email format validation
    if not re.match(email_pattern, EditEmailAddressEntry):
        app.infoBox("InvalidEmailErrorGuestEdit", "Error: Please enter a valid email address")
        return False
    if not EditPhoneNumberEntry.isdigit(): #Ensure phone number contains only numeric digits
        app.infoBox("PhoneNumberErrorGuestEdit", "Error: Phone number must contain only digits")
        return False
    if len(EditPhoneNumberEntry) != 11: #Enforce exactly 11 digits for the phone number
        app.infoBox("PhoneNumberLengthErrorGuestEdit", "Error: Phone number must be 11 digits")
        return False
    try:
        cur.execute("UPDATE tbl_guests SET FirstName = ?, LastName = ?, EmailAddress = ?, PhoneNumber = ? WHERE GuestID = ?",(EditFirstNameEntry, EditLastNameEntry, EditEmailAddressEntry, EditPhoneNumberEntry, SelectedGuestID)) #Update the guest record in the database with the new values
        con.commit() #Commit the update to permanently save changes
        app.infoBox("SuccessfulEdit", "Guest Sucessfully Updated")
        return True
    except sqlite3.IntegrityError: #Catch any database constraint errors during the update
        app.infoBox("DatabaseError", "Error: Could not insert into database")
        return False

def btnpress(btnName):
    global ForgottenPasswordOTP, SelectedRoomID #Access globals needed across multiple buttons
    if btnName == "Initial_Login":
        app.hide() #Hide the main/initial window
        app.showSubWindow("win_login")
    elif btnName == "Initial_SignUp":
        app.hide()
        app.showSubWindow("win_signup")
    elif btnName == "Login_SignUp":
        app.hideSubWindow("win_login")
        app.showSubWindow("win_signup")
    elif btnName == "Booking_Return":
        app.hideSubWindow("win_booking")
        ResetBookingGlobals() #Clear booking state when returning to main menu
        app.showSubWindow("win_mainmenu")
        SetCurrentDate()
    elif btnName == "Summary_Return":
        app.hideSubWindow("win_bookingsummary")
        ResetBookingGlobals() #Clear booking state when returning from the summary
        app.showSubWindow("win_mainmenu")
        SetCurrentDate()
    elif btnName == "Login_ForgotPassword":
        app.hideSubWindow("win_login")
        app.showSubWindow("win_forgotpassword")
    elif btnName == "ForgotPassword_Login":
        app.hideSubWindow("win_forgotpassword")
        app.showSubWindow("win_login")
    elif btnName == "ForgotPassword_EnterOTP":
        app.hideSubWindow("win_forgotpassword")
        if ForgottenPasswordValidation(): #Only send OTP if the entered email exists in the database
            SendForgottenOTP()
            app.showSubWindow("win_forgotpasswordotp")
        else:
            app.showSubWindow("win_forgotpassword") #Return to forgot password screen if email validation fails
    elif btnName == "ResendOTP":
        ResendForgottenOTP() #Resend the current OTP to the guest's email
    elif btnName == "ForgotPasswordOTP_ChangePassword":
        if ValidateForgottenOTP(): #Only proceed to change password if the OTP matches
            app.hideSubWindow("win_forgotpasswordotp")
            app.showSubWindow("win_changepassword")
    elif btnName == "ChangePassword_MainMenu":
        if ChangePasswordValidation(): #Only navigate away if the new password passes validation and is saved
            app.hideSubWindow("win_changepassword")
            app.showSubWindow("win_mainmenu")
            SetCurrentDate()
    elif btnName == "Login_MainMenu":
        app.hideSubWindow("win_login")
        if LoginDetailsValidation(): #Only show main menu if login credentials are valid
            app.showSubWindow("win_mainmenu")
            SetCurrentDate()
        else:
            app.showSubWindow("win_login") #Return to login screen on failed validation
    elif btnName == "Login_StaffLogin":
        app.hideSubWindow("win_login")
        app.showSubWindow("win_stafflogin")
    elif btnName == "SignUp_MainMenu":
        app.hideSubWindow("win_signup")
        if SignUpDetailsAppend(): #Only proceed to main menu if sign-up data is valid and inserted
            app.showSubWindow("win_mainmenu")
            SetCurrentDate()
        else:
            app.showSubWindow("win_signup")
    elif btnName == "MainMenu_Search":
        result = MainMenuCriteria() #Validate search criteria and query available rooms
        if result:
            HotelID, available_rooms = result #Retrieve the returned hotel ID and list of available rooms
            DisplayAvailableRooms(available_rooms) #Populate the booking window with buttons for each available room
            app.hideSubWindow("win_mainmenu")
            app.showSubWindow("win_booking")
    elif btnName.startswith("Booking_Room_"):
        roomid = int(btnName.split("_")[-1])
        SelectRoom(roomid)
    elif btnName == "Booking_Confirmation":
        if ConfirmBooking(): #Only show confirmation screen if the booking is successfully saved
            app.hideSubWindow("win_bookingsummary")
            app.showSubWindow("win_bookingconfirmation")
    elif btnName == "Confirm_MainMenu":
        app.hideSubWindow("win_bookingconfirmation")
        app.showSubWindow("win_mainmenu")
        SetCurrentDate()
    elif btnName == "Staff_Accounts":
        StaffLoadGuestTable() #Refresh the guest table data before displaying
        app.hideSubWindow("win_staffdisplay")
        app.showSubWindow("win_staffguests")
        StaffDisplayGuestTable() #Call display function to ensure table is up to date
    elif btnName == "Staff_Bookings":
        StaffLoadBookingTable() #Refresh the booking table data before displaying
        app.hideSubWindow("win_staffdisplay")
        app.showSubWindow("win_bookingtable")
        StaffLoadBookingTable() #Called again to ensure the table populates after the window is shown
    elif btnName == "GuestTable_Return":
        app.hideSubWindow("win_staffguests")
        app.showSubWindow("win_staffdisplay")
    elif btnName == "BookingTable_Return":
        app.hideSubWindow("win_bookingtable")
        app.showSubWindow("win_staffdisplay")
    elif btnName == "GuestAction_Delete":
        cur.execute("DELETE FROM tbl_guests WHERE GuestID = ?", (SelectedGuestID,)) #Delete the selected guest record from the database
        con.commit() #Commit the deletion permanently
        app.infoBox("DeleteSuccess", "Guest Successfully Deleted")
        app.hideSubWindow("win_guestaction")
        StaffLoadGuestTable() #Refresh the guest table to reflect the deletion
        app.showSubWindow("win_staffdisplay")
    elif btnName == "GuestAction_Return":
        app.hideSubWindow("win_guestaction")
        app.showSubWindow("win_staffguests")
    elif btnName == "GuestAction_Edit":
        LoadGuestEdit() #Preset the edit form with the current guest's data
        app.hideSubWindow("win_guestaction")
        app.showSubWindow("win_guestedit")
    elif btnName == "GuestEdit_Submit":
        if EditGuestDetailsAppend(): #Only return to guest table if edit validation and save succeeded
            app.hideSubWindow("win_guestedit")
            StaffLoadGuestTable() #Refresh the guest table to reflect the edit
            app.showSubWindow("win_staffguests")
    elif btnName == "BookingAction_Edit":
        LoadBookingEdit() #Preset the edit booking form with current booking data
        app.hideSubWindow("win_bookingaction")
        app.showSubWindow("win_bookingedit")
    elif btnName == "BookingAction_Delete":
        cur.execute("SELECT RoomID FROM tbl_bookings WHERE BookingID = ?", (SelectedBookingID,))
        SelectedDeletedRoomID = cur.fetchone()[0] #Retrieve the room ID of the booking being deleted
        cur.execute("DELETE FROM tbl_bookings WHERE BookingID = ?", (SelectedBookingID,))
        con.commit() #Commit the deletion
        app.infoBox("DeleteSuccess", "Booking Successfully Deleted")
        app.hideSubWindow("win_bookingaction")
        StaffLoadBookingTable() #Refresh the booking table to reflect the deletion
        app.showSubWindow("win_bookingtable")
    elif btnName == "BookingAction_Return":
        app.hideSubWindow("win_bookingaction")
        app.showSubWindow("win_bookingtable")
    elif btnName == "BookingEdit_Submit":
        if EditBookingAppend(): #Only return to booking table if edit validation and save succeeded
            app.hideSubWindow("win_bookingedit")
            StaffLoadBookingTable() #Refresh the booking table to reflect the edit
            app.showSubWindow("win_bookingtable")
    elif btnName == "BookingEdit_Return":
        app.hideSubWindow("win_bookingedit")
        app.showSubWindow("win_bookingaction")
    elif btnName == "GuestEdit_Return":
        app.hideSubWindow("win_guestedit")
        app.showSubWindow("win_staffguests")
    elif btnName == "SignUp_Login":
        app.hideSubWindow("win_signup")
        app.showSubWindow("win_login")
    elif btnName == "SignUp_PasswordRequirements":
        app.infoBox("PasswordRequirements", "Password must be at least 8 characters, includes a special character, includes a digit and includes an uppercase letter")
    elif btnName == "ChangePassword_PasswordRequirements":
        app.infoBox("PasswordRequirements", "Password must be at least 8 characters, includes a special character, includes a digit and includes an uppercase letter")
    elif btnName == "Staff_StaffDisplay":
        app.hideSubWindow("win_stafflogin")
        if StaffLoginDetailsValidation():
            app.showSubWindow("win_staffdisplay")
        else:
            app.showSubWindow("win_stafflogin")
    elif btnName == "Staff_Login":
        app.hideSubWindow("win_staffdisplay")
        app.showSubWindow("win_login")

def CreateInterface():
    ### Code For Initial Window ###
    app.setSize("Fullscreen")
    app.setFont(size=16)
    app.setBg("#f8f3e8") #Set the cream background colour for the initial window
    app.addLabel("InitialWindowTitle", "Welcome To Calor Hotels") #Add the welcome title label
    app.addNamedButton("Login","Initial_Login", btnpress)
    app.setButtonBg("Initial_Login", "#e83d1b")
    app.setButtonFg("Initial_Login", "#1a1a19")
    app.addNamedButton("Sign-Up","Initial_SignUp", btnpress)
    app.setButtonBg("Initial_SignUp", "#e83d1b")
    app.setButtonFg("Initial_SignUp", "#1a1a19")
    ### END Initial Window ###

    ### Code For Login Window ###
    app.startSubWindow("win_login")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("LoginTitle", "Login")
    app.addLabelEntry("Email Address:") #Input field for the guest's email on the login screen
    app.addLabelEntry("Password:", secret=True) #Input field for the guest's password on the login screen
    app.addNamedButton("Submit", "Login_MainMenu", btnpress)
    app.setButtonBg("Login_MainMenu", "#e83d1b")
    app.setButtonFg("Login_MainMenu", "#1a1a19")
    app.addNamedButton("Sign-Up", "Login_SignUp", btnpress)
    app.setButtonBg("Login_SignUp", "#e83d1b")
    app.setButtonFg("Login_SignUp", "#1a1a19")
    app.addNamedButton("Staff Login", "Login_StaffLogin", btnpress)
    app.setButtonBg("Login_StaffLogin", "#e83d1b")
    app.setButtonFg("Login_StaffLogin", "#1a1a19")
    app.addNamedButton("Forgotten Password", "Login_ForgotPassword", btnpress)
    app.setButtonBg("Login_ForgotPassword", "#e83d1b")
    app.setButtonFg("Login_ForgotPassword", "#1a1a19")
    app.stopSubWindow()
    ### END Login Window ###

    ### Code For Sign Up Window ###
    app.startSubWindow("win_signup")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("SignUpTitle", "SignUp")
    app.addLabelEntry("First Name:")
    app.addLabelEntry("Last Name:")
    app.addLabelEntry("Email Address")
    app.addLabelEntry("Password")
    app.addLabelEntry("Re-type Password:")
    app.addLabelEntry("Phone Number")
    app.addNamedButton("Password Requirements", "SignUp_PasswordRequirements", btnpress)
    app.setButtonBg("SignUp_PasswordRequirements", "#e83d1b")
    app.setButtonFg("SignUp_PasswordRequirements", "#1a1a19")
    app.addNamedButton("Submit", "SignUp_MainMenu", btnpress)
    app.setButtonBg("SignUp_MainMenu", "#e83d1b")
    app.setButtonFg("SignUp_MainMenu", "#1a1a19")
    app.addNamedButton("Login", "SignUp_Login", btnpress)
    app.setButtonBg("SignUp_Login", "#e83d1b")
    app.setButtonFg("SignUp_Login", "#1a1a19")
    app.stopSubWindow()
    ### END Sign Up Window ###

    ### Code For Forgotten Password ###
    app.startSubWindow("win_forgotpassword")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("ForgotPasswordTitle", "Forgotten Password")
    app.addLabelEntry("Please Enter Your Email Address:") #Input field for email on the forgot password screen
    app.addNamedButton("Return", "ForgotPassword_Login", btnpress)
    app.setButtonBg("ForgotPassword_Login", "#e83d1b")
    app.setButtonFg("ForgotPassword_Login", "#1a1a19")
    app.addNamedButton("Submit", "ForgotPassword_EnterOTP", btnpress)
    app.setButtonBg("ForgotPassword_EnterOTP", "#e83d1b")
    app.setButtonFg("ForgotPassword_EnterOTP", "#1a1a19")
    app.stopSubWindow()
    ### END FORGOTTEN PASSWORD WINDOW ###

    ### Code For Forgotten Password OTP ###
    app.startSubWindow("win_forgotpasswordotp")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("ForgotPasswordOTPTitle", "Forgot Password")
    app.addLabel("EnterOTPInstruction", "Please Enter the OTP That has been Sent to Your Email Address")
    app.addEntry("OTP_Entry") #Entry field where the guest types the OTP they received
    app.addNamedButton("Resend", "ResendOTP", btnpress)
    app.setButtonBg("ResendOTP", "#e83d1b")
    app.setButtonFg("ResendOTP", "#1a1a19")
    app.addNamedButton("Submit", "ForgotPasswordOTP_ChangePassword", btnpress)
    app.setButtonBg("ForgotPasswordOTP_ChangePassword", "#e83d1b")
    app.setButtonFg("ForgotPasswordOTP_ChangePassword", "#1a1a19")
    app.stopSubWindow()
    ### END FORGOTTEN PASSWORD OTP WINDOW ###

    ### Code For Change Password ###
    app.startSubWindow("win_changepassword")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("ChangePasswordTitle", "Change Password")
    app.addLabelEntry("Please Enter Your New Password:") #Input field for the guest's desired new password
    app.addLabelEntry("Please Re-Enter Your Password:") #Confirmation field to ensure the new password is typed correctly
    app.addNamedButton("Password Requirements", "ChangePassword_PasswordRequirements", btnpress)
    app.setButtonBg("ChangePassword_PasswordRequirements", "#e83d1b")
    app.setButtonFg("ChangePassword_PasswordRequirements", "#1a1a19")
    app.addNamedButton("Submit", "ChangePassword_MainMenu", btnpress)
    app.setButtonBg("ChangePassword_MainMenu", "#e83d1b")
    app.setButtonFg("ChangePassword_MainMenu", "#1a1a19")
    app.stopSubWindow()
    ### END CHANGE PASSWORD WINDOW ###

    ### Code For Staff Login ###
    app.startSubWindow("win_stafflogin")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("StaffLoginTitle", "Staff Login")
    app.addLabelEntry("Enter Your Staff Email Address:")
    app.addLabelEntry("Enter Your Staff Password:", secret=True)
    app.addNamedButton("Submit", "Staff_StaffDisplay", btnpress)
    app.setButtonBg("Staff_StaffDisplay", "#e83d1b")
    app.setButtonFg("Staff_StaffDisplay", "#1a1a19")
    app.addNamedButton("Return", "Staff_Login", btnpress)
    app.setButtonBg("Staff_Login", "#e83d1b")
    app.setButtonFg("Staff_Login", "#1a1a19")
    ### END STAFF LOGIN WINDOW ###

    ### Code For Staff Display ###
    app.startSubWindow("win_staffdisplay")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("StaffDisplayTitle", "Staff Display")
    app.addNamedButton("Guest Accounts", "Staff_Accounts", btnpress)
    app.setButtonBg("Staff_Accounts", "#e83d1b")
    app.setButtonFg("Staff_Accounts", "#1a1a19")
    app.addNamedButton("Booking Table", "Staff_Bookings", btnpress)
    app.setButtonBg("Staff_Bookings", "#e83d1b")
    app.setButtonFg("Staff_Bookings", "#1a1a19")
    app.stopSubWindow()
    ### END STAFF DISPLAY ###

    ### Code For Staff Guest Table ###
    app.startSubWindow("win_staffguests")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("GuestTableTitle", "Guest Accounts")
    app.addTable("GuestTable", ["ID", "First Name", "Last Name", "Email", "Password", "Phone Number"]) #Table widget to display all guest records
    app.addNamedButton("Action", "GuestActionBtn", GuestAction)
    app.setButtonBg("GuestActionBtn", "#e83d1b")
    app.setButtonFg("GuestActionBtn", "#1a1a19")
    app.addNamedButton("Return", "GuestTable_Return", btnpress)
    app.setButtonBg("GuestTable_Return", "#e83d1b")
    app.setButtonFg("GuestTable_Return", "#1a1a19")
    app.stopSubWindow()
    ### END STAFF GUEST TABLE ###

    ### Code For Staff Guest Action ###
    app.startSubWindow("win_guestaction")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("GuestActionTitle", "Guest Action")
    app.addNamedButton("Edit Details", "GuestAction_Edit", btnpress)
    app.setButtonBg("GuestAction_Edit", "#e83d1b")
    app.setButtonFg("GuestAction_Edit", "#1a1a19")
    app.addNamedButton("Delete Guest", "GuestAction_Delete", btnpress)
    app.setButtonBg("GuestAction_Delete", "#e83d1b")
    app.setButtonFg("GuestAction_Delete", "#1a1a19")
    app.addNamedButton("Return To The Guest Table", "GuestAction_Return", btnpress)
    app.setButtonBg("GuestAction_Return", "#e83d1b")
    app.setButtonFg("GuestAction_Return", "#1a1a19")
    app.stopSubWindow()
    ### END STAFF GUEST ACTION ###

    ### Code For Staff Edit Guest ###
    app.startSubWindow("win_guestedit")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("GuestEditTitle", "Edit Guest Details")
    app.addLabelEntry("Edit First Name:")
    app.addLabelEntry("Edit Last Name:")
    app.addLabelEntry("Edit Email Address:")
    app.addLabelEntry("Edit Phone Number:")
    app.addNamedButton("Submit Changes", "GuestEdit_Submit", btnpress)
    app.setButtonBg("GuestEdit_Submit", "#e83d1b")
    app.setButtonFg("GuestEdit_Submit", "#1a1a19")
    app.addNamedButton("Return To Guest Table", "GuestEdit_Return", btnpress)
    app.setButtonBg("GuestEdit_Return", "#e83d1b")
    app.setButtonFg("GuestEdit_Return", "#1a1a19")
    app.stopSubWindow()
    ### END STAFF EDIT GUEST ###

    ### Code For Staff Booking Table ###
    app.startSubWindow("win_bookingtable")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("BookingTableTitle", "Booking Records")
    app.addTable("BookingTable", ["Booking ID", "Guest ID", "Hotel ID", "Room ID", "Guest Count", "Arrival Date", "Departure Date"]) #Table widget to display all booking records
    app.addNamedButton("Action", "BookingActionBtn", BookingAction)
    app.setButtonBg("BookingActionBtn", "#e83d1b")
    app.setButtonFg("BookingActionBtn", "#1a1a19")
    app.addNamedButton("Return", "BookingTable_Return", btnpress)
    app.setButtonBg("BookingTable_Return", "#e83d1b")
    app.setButtonFg("BookingTable_Return", "#1a1a19")
    app.stopSubWindow()
    ### END STAFF BOOKING TABLE ###

    ### Code For Staff Booking Action ###
    app.startSubWindow("win_bookingaction")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("BookingActionTitle", "Booking Action")
    app.addNamedButton("Edit Booking", "BookingAction_Edit", btnpress)
    app.setButtonBg("BookingAction_Edit", "#e83d1b")
    app.setButtonFg("BookingAction_Edit", "#1a1a19")
    app.addNamedButton("Delete Booking", "BookingAction_Delete", btnpress)
    app.setButtonBg("BookingAction_Delete", "#e83d1b")
    app.setButtonFg("BookingAction_Delete", "#1a1a19")
    app.addNamedButton("Return", "BookingAction_Return", btnpress)
    app.setButtonBg("BookingAction_Return", "#e83d1b")
    app.setButtonFg("BookingAction_Return", "#1a1a19")
    app.stopSubWindow()
    ### END STAFF BOOKING ACTION ###

    ### Code For Staff Edit Booking ###
    app.startSubWindow("win_bookingedit")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("BookingEditTitle", "Edit Booking")
    app.addLabelOptionBox("Edit Guest Count", ["1","2","3","4","5","6"])
    app.addLabelOptionBox("Edit Location:", ["London Riverside","Manchester","Birmingham Broad Street","Lake District","Cotswolds","Yorkshire Dales","Oxford","Bath","Cantebury", "Cornwall"])
    app.addLabel("Edit Date of Arrival")
    app.addDatePicker("Edit Arrival Date")
    app.setDatePickerRange("Edit Arrival Date",2026,2028)
    app.addLabel("Edit Date of Departure")
    app.addDatePicker("Edit Departure Date")
    app.setDatePickerRange("Edit Departure Date",2026,2028)
    app.addLabelOptionBox("Edit Room Type", ["Single Bed","Double Bed","2 Double Bed","King Bed","2 Queen"])
    app.addNamedButton("Submit", "BookingEdit_Submit", btnpress)
    app.setButtonBg("BookingEdit_Submit", "#e83d1b")
    app.setButtonFg("BookingEdit_Submit", "#1a1a19")
    app.addNamedButton("Return", "BookingEdit_Return", btnpress)
    app.setButtonBg("BookingEdit_Return", "#e83d1b")
    app.setButtonFg("BookingEdit_Return", "#1a1a19")
    app.stopSubWindow()
    ### END STAFF EDIT BOOKING ###

    ### Code For Main Menu ###
    app.startSubWindow("win_mainmenu")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("MainMenuTitle", "Main Menu")
    app.addLabelOptionBox("Guest Count", ["1", "2", "3", "4", "5", "6"])
    app.addLabelOptionBox("Enter Branch Location", ["London Riverside","Manchester","Birmingham Broad Street","Lake District","Cotswolds","Yorkshire Dales","Oxford","Bath","Cantebury", "Cornwall"])
    app.addLabel("Enter Date of Arrival")
    app.addDatePicker("Date Of Arrival")
    app.setDatePickerRange("Date Of Arrival",2026,2028)
    app.addLabel("Enter Date of Departure")
    app.addDatePicker("Date Of Departure")
    app.setDatePickerRange("Date Of Departure",2026,2028)
    app.addLabelOptionBox("Room Type", ["Single Bed", "Double Bed", "2 Double Bed", "King Bed", "2 Queen"])
    app.addNamedButton("Search", "MainMenu_Search", btnpress)
    app.setButtonBg("MainMenu_Search", "#e83d1b")
    app.setButtonFg("MainMenu_Search", "#1a1a19")
    app.stopSubWindow()
    ### END Main Menu ###

    ### Code For Booking ###
    app.startSubWindow("win_booking")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("BookingTitle", "Booking") #Placeholder title, window is dynamically rebuilt with room buttons upon run
    app.stopSubWindow()
    ### END Booking ###

    ### Code For Booking Summary ###
    app.startSubWindow("win_bookingsummary")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("BookingSummaryTitle", "Booking Summary")
    app.addLabel("GuestCountSummary", "Guest Count:...") #Placeholder updated dynamically with guest count
    app.addLabel("LocationSummary", "Location:.....") #Placeholder updated dynamically with chosen location
    app.addLabel("RoomTypeSummary", "Room Type:.....") #Placeholder updated dynamically with room type
    app.addLabel("ArrivalSummary", "Arrival:.....") #Placeholder updated dynamically with arrival date
    app.addLabel("DepartureSummary", "Departure:.....") #Placeholder updated dynamically with departure date
    app.addNamedButton("Confirm Booking", "Booking_Confirmation", btnpress)
    app.setButtonBg("Booking_Confirmation", "#e83d1b")
    app.setButtonFg("Booking_Confirmation", "#1a1a19")
    app.addNamedButton("Return To Main Menu", "Summary_Return", btnpress)
    app.setButtonBg("Summary_Return", "#e83d1b")
    app.setButtonFg("Summary_Return", "#1a1a19")
    app.stopSubWindow()
    ### END BOOKING SUMMARY ###

    ### Code For Booking Confirmation ###
    app.startSubWindow("win_bookingconfirmation")
    app.setSize("Fullscreen")
    app.setBg("#f8f3e8")
    app.addLabel("BookingConfirmationText", "Booking Has Been Confirmed")
    app.addLabel("BookingConfirmationEmailText", "An Email Will Be Sent With Further Details Shortly")
    app.addNamedButton("Return to Main Menu", "Confirm_MainMenu", btnpress)
    app.setButtonBg("Confirm_MainMenu", "#e83d1b")
    app.setButtonFg("Confirm_MainMenu", "#1a1a19")
    app.stopSubWindow()
    ### END BOOKING CONFIRMATION ###

cur.execute("DELETE FROM tbl_bookings")
cur.execute("DELETE FROM tbl_guests")
con.commit()
CreateInterface() #Build the entire GUI interface by calling the setup function
app.go() #Start the appJar event loop and display the application window
