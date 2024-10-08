'''

Dream Journal Assistance Application

Author: Ranbir Singh Deol

Latest Update: 08/29/2024

'''

# Modules

import os 
import shutil
import subprocess
from datetime import datetime 
import re
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Directories

# To run the program, you must put your journal directory here
# Get the directory of the current script
SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Navigate to the parent directory of 'src' which is 'dream-vault'
LOCAL_DIRECTORY = (os.path.dirname(SCRIPT_DIRECTORY))

JOURNAL_DIRECTORY = os.path.join(LOCAL_DIRECTORY, 'journal')
BACKUP_DIRECTORY = os.path.join(LOCAL_DIRECTORY, 'backups')

# These are included in the program file
LOGS_FILE = os.path.join(LOCAL_DIRECTORY, 'logs.txt')
TEMPLATE_DIRECTORY = os.path.join(LOCAL_DIRECTORY, 'template.txt')
SYNC_DIRECTORY = os.path.join(LOCAL_DIRECTORY, 'sync.txt')

'''
This variable is very special, this should only be set to 'True', if you are syncing backup
Data, from a program that is not this one. Hence, it will uses newlines, to create a readable
Template, otherwise, keep this false, if you are only backing up or syncing with this program
'''
SYNC_EXTERNAL = False

# Color Codes

class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Constants

# The programs name that will be displayed
PROGRAM_NAME =  Color.GREEN + "Dream Journal Assistance\n" + Color.END
# The text editor to be used to open entries
TEXT_EDITOR = ["emacs", "-nw"]
# Words per line for every dream entry that is from a sync
DREAM_CUTOFF = 20

# A list of all the months, to be used to convert number month to word month
MONTHS = [
    None, 'January', 'February', 'March', 'April', 'May', 
    'June', 'July', 'August', 'September', 'October', 'November', 'December'
]

# A list of all the months mapped to a number, used to convert word months to numbers
MONTHS_REVERSED = {
    "January": '01',
    "February": '02',
    "March": '03',
    "April": '04',
    "May": '05',
    "June": '06',
    "July": '07',
    "August": '08',
    "September": '09',
    "October": '10',
    "November": '11',
    "December": '12'
}

# A list of location generic error messages that don't require variables do be displayed
ERROR_MESSAGES = [
    f"{Color.RED} {Color.END}",
    f"{Color.RED}Error!: [Invalid Day, Month, or Year]{Color.END}",
    f"{Color.RED}Error!: [Invalid File Name]{Color.END}",
    f"{Color.RED}Error!: [Invalid Title]{Color.END}",
    f"{Color.RED}Error!: [Unable To Create Dream Entry]{Color.END}",
]

# Lists of values that can be auto selected from the title, and inserted into the statisitcs of an entry
DREAM_TYPES = ['Normal', 'Lucid', 'Nightmare', 'Vivid']
TECHNIQUES = ['None', 'WILD', 'DILD', 'SSILD', 'MILD']
SLEEP_CYCLE = ['Regular', 'WBTB']

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# [✅]
def check_folder_exists(folder_directory, folder_name):
    """
    Check if a specific folder exists within a directory.

    Args:
        folder_directory (str): The path to the parent directory.
        folder_name (str): The name of the folder to check.

    Returns:
        bool: True if the folder exists, False otherwise.
    """

    # Create the full path to the folder
    folder_path = os.path.join(folder_directory, folder_name)
    
    # Check if the folder exists
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        return True
    else:
        return False

# [✅]
def create_folder(folder_directory, folder_name):
    """
    Create a folder in a specific directory, with a specific name

    Args:
        folder_directory (str): The path to the parent directory.
        folder_name (str): The name of the folder to create.

    Returns:
        bool: True if the folder was created, False otherwise.
    """

    try:
        # Creating the directory location
        new_folder = os.path.join(folder_directory, folder_name)

        # Making the directory in our new folder
        os.makedirs(new_folder)

        return True
    # Display an error in RED
    except OSError as e:
        print(f"\n{Color.RED}{e}{Color.END}\n")

        return False

# [✅]
def create_dream(year, month, day, title, content, backup):
    """
    Main function that creates a dream. Here we set up the dream, and
    either are syncing from a backup file, or manually creating a new entry.

    Args:
        -- [Used to manually create  a entry]
        year (str): The year this entry was created
        month (str/int): The month this entry was createad
        day (str): The day this entry was created
        file_name (str): The file's name
        -- [Used to load a backup]
        title (str): The title of the dream
        content (str): The body / main content of the entry
        -- 
        modify_file(bool): If we want to modify the statistics inside the file manually

    Returns:
        bool: True if the entry was created, otherwise False
    """

    # First we must check if we have valid variables
    try:
        # We must cast the month into an integer, avoiding any Strings
        day = int(day)
        month = int(month)
        year = int(year)

        entry_title = ''

        # Let's check if we have a valid year, and day
        # Year: 1000 - 10000
        # Day: 1 - 31
        # Month: 1 - 12
        if not (year >= 999 and year <= 9999 and day <= 31 and day >= 1 and month <= 12 and month >= 1):
            return ERROR_MESSAGES[1]
        
        # Let's cast all the variables into their proper formats
        year = str(year)
        month = str(MONTHS[month])
        day = str(day) 

        # Let's check if we have this path created
        if not check_folder_exists(JOURNAL_DIRECTORY, year):
            create_folder(JOURNAL_DIRECTORY, year) 

        # Checking if we have the month directory inside our year_directory
        year_directory = os.path.join(JOURNAL_DIRECTORY, year)
        if not check_folder_exists(year_directory, month):
            create_folder(year_directory, month)
        
        # Checking if we have the day directory inside our month_directory
        month_directory = os.path.join(JOURNAL_DIRECTORY, str(year), month)
        if not check_folder_exists(month_directory, day):
                create_folder(month_directory, day)

        # Turning our dream title into a file name
        file_name = str(title).lower().replace(' ', '_')[0:25]

        # If we don't have a valid, we won't be able to create our path
        if not file_name or len(file_name) <= 0:
            return (ERROR_MESSAGES[2])
            
        # Let's remove /'s from file names so we don't search the wrong directory
        file_name = file_name.replace('/', '_')
        file_name = file_name.replace('?', '_')
        file_name = file_name.replace(':', '_')

        # Creating our destination path
        destination_path = os.path.join(month_directory, str(day), f"{file_name}.txt")

        # Formatted file day: xx xxxx, xxxx
        file_date = f"{day} {month}, {year}"

        if backup:
            # We're loading a backup, we just want to clone the content into the file           
            with open(destination_path, 'w') as dream_entry:
                # First we'll add the date
                dream_entry.write(f"[ ({title}) | ({file_date}) ]\n")
                # Then we'll add the content
                dream_entry.write(content)

                with open(destination_path, 'a') as dream_entry:
                    # Closing the entry off with a line
                    dream_entry.write('\n───────────────────────────────────────────────────────────────────────')
        
        # We're creating a new journal entry
        else:
            # Let's clone the template format into our file
            with open(TEMPLATE_DIRECTORY, 'r') as template:
                template_content = template.read() 

            # Replace the place holder date, with our formatted file date
            template_content = template_content.replace('DATE_HERE', file_date)

            # Replace the title of the dream
            template_content = template_content.replace('TITLE_HERE', title)

            # Dream Inputs, and writing them to a file
            dream_type = input("Enter a dream type (Normal, Lucid, Vivid, Nightmare, No Recall): ")
            template_content = template_content.replace('dream_type', dream_type)

            dream_tech = input("Enter a dream technique (None, WILD, SSILD): ")
            template_content = template_content.replace('dream_tech', dream_tech)

            sleep_cycle = input("Enter a sleep cycle (Regular, WBTB): ")
            template_content = template_content.replace('dream_cycle', sleep_cycle)

            # Creating our dream entry, and setting it to our template's content
            with open(destination_path, 'w') as dream_entry:
                dream_entry.write(template_content)

            # Asking the user if they'd like to edit the dream and edit it
            while True:
                open_file_edit = input("Would you like to open and edit dream entry (y / n): ").strip().lower()
                if open_file_edit == 'y':
                    subprocess.run(TEXT_EDITOR + [destination_path])
                    break
                elif open_file_edit == 'n':
                    break
                else:
                    print(f"\n{Color.RED}Unknown Command{Color.END}: [{open_file_edit}]\n")

        # Logging this dream entry creation to our logs.txt
        log("Created Dream @", destination_path)

        return True

    except Exception as e:
        print(f"{Color.RED}Error! [{e}]{Color.END}")

        return False

# [✅]
def create_entry():
    """
    This function creates a dreamy entry from user input,
    it must have a valid create_dream() function to work

    Returns:
        bool: True if the entry was created, otherwise False
    """

    # Changing our directory to our journal directory
    os.chdir(JOURNAL_DIRECTORY)
    
    # We'll use a while loop to continue asking for valid input
    while True:

        # Ask the user for a valid YYYY/MM/DD or ask them if they want to quit
        user_input = input("\nEnter a date (YYYY/MM/DD) or ('q' to quit creation): ")

        # If the date matches the format: xxxx/xx/xx, let's create the entry
        if re.match(r'^\d{4}/\d{2}/\d{2}$', user_input):
            try:
                # Attempt to create a datetime object from the input string
                year, month, day = map(int, user_input.split('/'))

                # Let's check if we have a valid date
                date_obj = datetime(year, month, day)

                # Validate the day of the month
                if date_obj.year != year or date_obj.month != month or date_obj.day != day:
                    return
                
                # Getting a name for the dream
                while True:
                    entry_title = input("Enter a title for your dream entry: ")
                    if len(entry_title) >= 1:
                       # Let's create our dream, and open it for the user
                        creation_bool = create_dream(year, month, day, entry_title, None, False)
                        break
                    else:
                        print(ERROR_MESSAGES[3])

                if creation_bool:
                    # Open up the navigation menu after creating the dream
                    navigate()
                else:
                    print(ERROR_MESSAGES[4])

                # End the loop
                break

            except ValueError as e:
                # If a ValueError is raised, the input is not a valid date, not critical, so we'll print in yellow
                print(f"\n{Color.YELLOW}{e}{Color.END}") 

        # If the user wants to exit, let's break the loop
        elif user_input == 'q':
            print(f"\n{Color.YELLOW}Cancelling Dream Creation{Color.END}\n")
            break
        
        print(f"\n{Color.YELLOW}Invalid Date, Try Again!{Color.END}")

# [✅]
def delete_entry(file_path):
    """
    This function check a certain file path,
    and deletes all empty files, starting from child,
    then we search it's parent, and then the grandparent

    Arguments:
        file_path (str): The location of our file

    Returns:
        True is we deleted the file, False if we encountered an error
    """

    try:
        # Let's first get our current directory
        dir_path = os.path.dirname(file_path)

        # Try to do os.remove with the file path
        os.remove(file_path)

        # Log the deletion
        log("Deleted Dream @", file_path)

        # Check if the directory is empty
        if not os.listdir(dir_path):

            # Remove the directory if it's empty
            os.rmdir(dir_path)

            # Log the deletion
            log("Removed Directory", dir_path)

            # Month Directory
            parent_dir = os.path.dirname(dir_path)

            # Chekc if the month directory is empty
            if not os.listdir(parent_dir):

                # Remove the directory if it's empty
                os.rmdir(parent_dir)

                # Log the deletion
                log("Removed Directory", parent_dir)

                # Year Directory
                grand_parent_dir = os.path.dirname(parent_dir)

                # Check if the year directory is empty
                if not os.listdir(grand_parent_dir):

                    # Remove the directory if it's empty
                    os.rmdir(grand_parent_dir)

                    # Log the deletion
                    log("Removed Directory", grand_parent_dir)

                    return True

    # Log the error if we couldn't delete a dream
    except OSError as e:
        log("Failed To Delete Dream @", file_path)
        return False

# [✅]
def date_formatter(date_unformatted, flipped, bracketBug):
    """
    Formatting a date into the numerical version:
    eg. [Day Month, Year] -> [YYYY/MM/DD] (1) | Or [Month Day, Year] -> [YYYY/MM/DD] (2)
    (1) is used for creation, (2) is used for the syncing [backup file is in month day]

    Arguments:
        date_unformatted (str): The unformatted date
        flipped (bool): If we either want (1) True or (2) False
        
    Returns:
        The date formatted in the method requested, or 'DirtyEntry', meaning that the string was malformed
    """

    try: 

        # Splitting date using ','
        parts = date_unformatted.split(',')

        # Variables to store our formatted day, month, and year
        day = ''
        month = ''
        year = ''

        # Checking if we have a split of 2 parts [Day Month, Year]
        if len(parts) == 2:
            # We have [Month Day, Year]
            
            if flipped:
                # Getting the day and month, also removing the starting '('
                day_month = parts[0].strip().removeprefix('(')
                # Getting the year
                year = parts[1].strip()

                print(year)
                
                # Extracting day and month
                day_month_parts = day_month.split()

                # Checking if we have two parts
                if len(day_month_parts) == 2:
                    # Our month
                    month = day_month_parts[0].strip()
                    # Our day
                    day = day_month_parts[1].strip() 
                    # Checking if we have a valid month
                    if month in MONTHS_REVERSED:
                        if day.isdigit() and 1 <= int(day) <= 31:
                            formatted_date = f"{year}-{MONTHS_REVERSED[month]}-{day}"
                            return formatted_date
                        
            # We have [Day Month, Year]
            else:
                # Getting the day and month, and removing the starting '('
                day_month = parts[0].strip().removeprefix('(')
                # The year, minus a ')' bracket at the end
                if bracketBug:
                    year = parts[1].strip()[:-1]
                else:
                    year = parts[1].strip()
                
                # Extracting day and month
                day_month_parts = day_month.split()

                # Checking if we have a valid split
                if len(day_month_parts) == 2:
                    # Day part
                    day = day_month_parts[0].strip()  
                    # Month part  
                    month = day_month_parts[1].strip()
                    
                    # Checking if this month exists
                    if month in MONTHS_REVERSED:
                        if day.isdigit() and 1 <= int(day) <= 31:
                            formatted_date = day + "-" + str(MONTHS_REVERSED[month]) + "-" + year
                            return formatted_date

    # Return error and 'DirtyEntry', also log the error
    except Exception as e:
        log('Malformed Date!', date_unformatted)
        return 'DirtyEntry'
    
    # We got to the end without raising an error or returing
    # Throw an error and return 'DirtyEntry'
    log('Malformed Date!', date_unformatted)
    return 'DirtyEntry'

# [✅]
def list_files(directory):
    """
    A function that searches every file within a directory

    Arguments:
        directory (str): The directory we want to search
        
    Returns:
        All the files organized by date [Newest -> Oldest]
        Sort Check: Year, Month, Day
    """

    # List to store our files
    files = []

    # Loop through all the dream files
    for root, _, file_names in os.walk(directory):

        # Looping throw all the files
        for file_name in file_names:

            # If we have a .txt
            if file_name.endswith(".txt"):

                # We'll want to create the path
                file_path = os.path.join(root, file_name)

                # Then we'll get the date from the entry.txt
                date = extract_date_from_file(file_path)
                
                # Check if we have a valid date
                date = date_formatter(date, False, True)

                # If our date isn't a malformed date
                if date != 'DirtyEntry':
                    # If the date exists, let's add it to our files
                    if date:
                        files.append((date, file_path))
                elif date == 'DirtyEntry':
                    files.append(('01-01-0001', file_path))

    # Sort files by date in descending order (newest to oldest)
    # It first checks year, month, and then date, and then we reverse and set
    files.sort(key=lambda date: datetime.strptime(date[0], "%d-%m-%Y"), reverse=True)

    # Return our list of files
    # Ex: files = [('file1', '/path/to/file1.txt'),..
    return [file_path for _, file_path in files]

# [✅]
def extract_date_from_file(file_path):
    """
    A function that extracts the dream date from a file

    Arguments:
        file_path (str): The files path, so that we can read it
        
    Returns:
        The date, if we have it inside the file, othewise return 'DirtyEntry',
        so that we don't accidentally crash the program
    """
    try:
        # Pattern to match date after inital '|'
        # Eg. [ (Title) | (X) ]
        date_pattern = r"\[.*\| (.*) \]" 

        # We'll then open that file in read mode
        with open(file_path, 'r') as file:
            
            # Read the content
            content = file.read()

            # Check if we have the date pattern inside the content
            match = re.search(date_pattern, content)
            if match:
                # Let's return the date
                return match.group(1)
            else:
                # Throw an error if the date is missing, and log it
                log("Date Missing In", file_path)
                print("───────────────────────────────────────────────────────────────────────")
                print(f"{Color.RED}Critical Error! Date Missing In: {file_path}\n1. Set Title To: [ (TITLE) | (DATE) ]\n3. Do Not Forget Spaces!\n4. Use 'r' Command To Refresh\n5. Error Should Be Resolved{Color.END}")
                return 'DirtyEntry'
            
    # We've caught an error
    except Exception as e:
        # Display an error, log the error, and return 'DirtyEntry'
        log("Date Missing In", file_path)
        print("───────────────────────────────────────────────────────────────────────")
        print(f"{Color.RED}Critical Error! Date Missing In: {file_path}\n1. Set Title To: [ (TITLE) | (DATE) ]\n3. Do Not Forget Spaces!\n4. Use 'r' Command To Refresh\n5. Error Should Be Resolved{Color.END}")
        return 'DirtyEntry'

# [✅]
def display_dream(file_path, openEditor):
    """
    A function that displays a dream to the console

    Arguments:
        file_path (str): The files path, so that we can read it
        openEditor (str): If we want to edit the file or not
        
    Returns:
        True is everything was displayed correctly, False if an error occured
    """

    try:
        # Open the file with reader
        with open(file_path, 'r') as file:

            # If editor is False, read it to the console only
            if openEditor == False:
                # We must check if it has a valid date, we'll display the error to the user, so that they can fix it
                if (date_formatter(extract_date_from_file(file_path), False, True) == 'DirtyEntry'):
                    print("───────────────────────────────────────────────────────────────────────")
                    print(f"{Color.RED}Malformed Date!:\n1. Change Date To A Valid: [Day Month, Year]\n2. Use 'r' Command To Refresh\n3. Error Should Be Resolved{Color.END}")
                # Otherwise, normally print to the screen
                content = file.read()
                print(content)
                return True
            # If editor is True, let's open it with our text editor
            else:
                subprocess.run(TEXT_EDITOR + [file_path])
                return True

    # If an error occurs print it, log it, and then return False
    except Exception as e:
        log("Unknown Error", e)
        print(f"{Color.RED}Error! {e}{Color.END}")
        return False

# [✅]
def navigate():
    """
    A function that can navigate through every dream inside our journal,
    using CLI, and certain commands the user can use. Moreover, the 
    navigation is wrapped, meaning that if we are at the end, we'll wrap
    to the start again, hence we cannot crash this function.

    Commands:
        [n]ext: Go to the next file
        [p]revious: Go to the previous file
        [e]dit: Edit the current file
        [d]elete: Delete the current file
        [r]efresh: Refresh the current file
        [i]ndex: Change index
        [c]lear logs: Clear local logs
        [q]uit: Quit navigation

    Returns:
        Nothing
    """

    # A variable to store all our local error logs
    error_log = []

    # A file that stores all of our files inside of our journal directory
    dream_files = list_files(JOURNAL_DIRECTORY)

    # There are no files, let's display that we don't have any entries
    if not dream_files:
        print(f"\n{Color.YELLOW}No Dream Entries Found!{Color.END}\n")
        return

    # Index to keep track of what file we are looking at currently
    index = 0

    # Main display loop
    while True:

        # Let's first clear the terminal
        clear_terminal()

        # Let's check if we have a negative index
        if index < 0:
            # Set it to zero, [avoiding crashses]
            index = 0

        # Otherwise, if it's greater than the amount of files we have, remove 1, which wraps around to the start
        elif index >= len(dream_files):
            index = len(dream_files) - 1

        # Dream Count Display
        print(f"\n{Color.BLUE}Dream: [{index + 1}/{len(dream_files)}]{Color.END} | @ {dream_files[index]}\n\n───────────────────────────────────────────────────────────────────────")
        
        # Display the latest dream
        display_attempt = display_dream(dream_files[index], False)
        if not display_attempt:
            error_log.append((f"\n{Color.RED}Failed To Display Entry!{Color.END}: [{dream_files[index]}]\n"))

        # Displaying errors in the local log
        for item in error_log:
            print(item)
        
        # Command prompt
        print("───────────────────────────────────────────────────────────────────────\n")
        print(f"{Color.GREEN}Commands: [n]ext, [p]revious, [e]dit, [d]elete, [r]efresh, [i]ndex, [c]lear logs, [q]uit{Color.END}")
        
        # Command input, make it lower, and remove spaces
        command = input("\nEnter a command: ").strip().lower()

        # If the user wants to go next
        if command == 'n':
            # Increment the index, % to make sure we're not over the amount of files we have
            index = (index + 1) % len(dream_files)
        elif command == 'p':
            # Decrement the index, % to make sure we can wrap
            index = (index - 1) % len(dream_files)
        elif command == 'e':
            # Display our dream, with editing on
            display_dream(dream_files[index], True) 
        elif command == 'd':
            # Delete a dream entry
            delete_entry(dream_files[index])

            # Update list of files after deletion
            dream_files = list_files(JOURNAL_DIRECTORY) 

            # If there a no dream files, throw and errors
            if not dream_files:
                print(f"\n{Color.YELLOW}No Dream Entries Found!{Color.END}\n")
                break
            # Otherwise, if the length is greater, decrement it
            if index >= len(dream_files):
                index = len(dream_files) - 1

        # If the command is to refresh, we'll load the file again
        elif command == 'r':
            # If the path exists still
            if os.path.exists(dream_files[index]):
                # Clear terminal
                clear_terminal()
                # Display the current dream we're on
                display_attempt_refresh = display_dream(dream_files[index], False)

                # Failed to display
                if not display_attempt_refresh:
                    error_log.append((f"\n{Color.RED}Failed To Display Entry!{Color.END}: [{dream_files[index]}]\n"))

        # If the command is to index to a certain dream location
        elif command == 'i':
            # Getting our index location we want to navigate to
            index_location = input("Enter an index location: ")
            try:
                index_location = int(index_location)
                # Check if index_location is within the valid range
                if 0 <= index_location <= len(dream_files):
                    # Set our index to the proper location, subract 1, index's start at 0
                    index = index_location - 1
                else:
                    # Handle invalid index input
                    error_log.append((f"\n{Color.RED}Invalid Index!{Color.END}: [{index_location}]\n"))
            except Exception as e:
                error_log.append((f"\n{Color.RED}Invalid Index!{Color.END}: [{index_location}]\n"))
        # If our command is to clear our local logs, set the error_logs to empty
        elif command == 'c':
            error_log = []
        # If the command is to quit, break the navigation loop
        elif command == 'q':
            # Quit the loop
            break
        # Otherwise, we have an invalid error, display this
        else:
            # Display we have an invalid command
            error_log.append((f"\n{Color.RED}Unknown Command{Color.END}: [{command}]\n"))

# [✅]
def sync():
    """
    Sync loads a .txt fiFe and reads all the contents. It then
    turns the text inside the body into a dream journal. There is
    a specific format to be followed, and this format is used in 'backup()'

    Returns:
        Nothing
    """

    # A count to store how many files we've created
    files_created_count = 0

    try:
        # Open our sync.txt and read its contents
        with open(SYNC_DIRECTORY, 'r') as file:
            content = file.readlines()

        # Variable to store all entries in an organized manner
        organized_entries = []

        # Temporary variable to store the local entry
        entry = None
        capture_body = False

        if SYNC_EXTERNAL == False:
            # Loop through every line in our sync.txt
            for line in content:
                # Remove leading and trailing spaces
                line = line.strip()

                # Check if the line starts with our delimiter
                if line == "==============================":
                    # Check if an entry exists and append it to organized_entries
                    if entry and entry["Body"]:
                        organized_entries.append(entry)
                    # Initialize a new entry
                    entry = {"Date": "", "Title": "", "Body": ""}
                    capture_body = False

                # If we have an entry
                elif entry is not None:
                    if line.startswith("[ (") and "|" in line:
                        # Extract title and date
                        parts = line.split("|")
                        entry["Title"] = parts[0].strip("[ (")[:-1].strip()
                        entry["Date"] = parts[1].strip(") ]")[1:].strip()
                    elif line.startswith("───────────────────────────────────────────────────────────────────────"):
                        capture_body = True
                        if entry["Body"]:
                            entry["Body"] += "\n"
                        entry["Body"] += line
                    elif capture_body:
                        if entry["Body"]:
                            entry["Body"] += "\n"
                        entry["Body"] += line

            # If we have a valid entry at the end of the file, append it to organized_entries
            if entry and entry["Body"]:
                organized_entries.append(entry)

            # Loop through the entries, and create a journal .txt for each
            for entry in organized_entries:
                try:
                    # We'll split our date, to check if it is valid
                    day, month, year = date_formatter(entry['Date'], False, False).split('-')
                    # Make sure we don't have a bad entry
                    if year == 'DirtyEntry' or month == 'DirtyEntry' or day == 'DirtyEntry':
                        print(f"{Color.RED}Invalid Entry: {entry['Title']}{Color.END}")
                    else:
                        # If everything is valid, let's create our dream
                        create_dream(year, month, day, entry['Title'], entry['Body'], True)
                        # Add it to the total
                        files_created_count += 1
                except Exception as e:
                    print(f"\n{Color.RED}Syncing Failed! {e}{Color.END}\n")
        else:
            # Loop through every line in our sync.txt
            for line in content:
                # Remove spaces
                line = line.strip()

                # Check if the line starts with our delimiter
                if line.startswith("=============================="):

                    # Check if an entry exists
                    if entry:
                        # Clean up leading/trailing spaces in title and body
                        if "Title" in entry:
                            # Title, Date, and then the rest is the body
                            entry["Title"] = entry["Title"].strip()
                            entry["Body"] = entry["Body"].strip()
                            organized_entries.append(entry)

                    # If we don't have an entry, let's set one up
                    entry = {"Date": "", "Title": "", "Body": ""}
                
                # Otherwise if we have an entry
                elif entry:
                    # If we don't have a date
                    if not entry["Date"]:
                        # Grab the date
                        entry["Date"] = line.strip()
                    # If we don't have a title
                    elif not entry["Title"]:
                        # Grab the title
                        entry["Title"] = line.strip()
                    # Otherwise
                    else:
                        if line: 
                            # Only add non-empty lines to body
                            if entry["Body"]:
                                entry["Body"] += "\n"
                            entry["Body"] += line

            # If we have a valid entry
            if entry:
                # Clean up leading/trailing spaces in title and body for the last entry
                if "Title" in entry:
                    entry["Title"] = entry["Title"].strip()
                    entry["Body"] = entry["Body"].strip()
                    organized_entries.append(entry)
            # Loop through the entries, and create a journal .txt for each
            for entry in organized_entries:
                try:
                    # FIX HERE
                    year, month, day = date_formatter(entry['Date'], False, False).split('-')
                    formatted_title = str(entry['Title']).lower().replace(' ', '_')[0:25]
                    if year == 'DirtyEntry' or month == 'DirtyEntry' or day == 'DirtyEntry':
                        print(f"Invalid Entry :{entry['Title']}")
                    else:
                        log("Creating the dream: ", entry['Title'])
                        #create_dream(year, month, day, formatted_title, entry['Title'], entry['Body'], False)
                except Exception as e:
                    print(e)

    except Exception as e:
        print(f"Error? {e}")

    # Log the total files created
    log("Sync.txt Was Loaded! Files Created", files_created_count)

    # Display that we were able to sync
    print(f"\n{Color.GREEN}Syncing Was Completed Successfully!{Color.END}\n")

# [✅]
def backup():
    '''
    Backs up the dream journal files and sends the backup via email.
    '''

    # Let us get all the dream files
    dream_files = list_files(JOURNAL_DIRECTORY)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  # Adjusted timestamp format
    backup_file_name = f"[{timestamp}]_Dream_Backup.txt"
    output_file_path = os.path.join(BACKUP_DIRECTORY, backup_file_name)

    with open(output_file_path, 'a') as output_file:
        output_file.write("==============================\n")

    # Checking if we have any dreams
    if not dream_files:
        print(f"\n{Color.YELLOW}No Dream Entries Found{Color.END}\n")
    else:
        for file_path in dream_files:
            log("Backing Up File", file_path)

            with open(file_path, 'r') as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    if line.startswith("[ ("):
                        match = re.search(r'\[ \((.*?)\) \| \((.*?)\) \]', line)
                        if match:
                            title = match.group(1)
                            date_str = match.group(2)
                            formatted_output = f"[ ({title}) | ({date_str}) ]\n"

                            # Join all lines except the last one in rest_of_content
                            rest_of_content = ''.join(lines[i + 1:])

                            full_output = formatted_output + rest_of_content

                            with open(output_file_path, 'a') as output_file:
                                output_file.write(full_output)
                                output_file.write("\n==============================\n")
    while True:
        # Ask the user if they want to recieve an email
        ask_to_send = input("Do you want to export this backup file? (y | n): ")
        if (ask_to_send == 'y'):
            send_email(output_file_path)
            break
        elif (ask_to_send == 'n'):
            break
        else:
            print((f"\n{Color.RED}Unknown Command{Color.END}: [{ask_to_send}]\n"))

    # Open the backup file with the text editor
    if output_file_path:
        subprocess.run(TEXT_EDITOR + [output_file_path])
    else:
        print(f"\n{Color.RED}No backup file was created.{Color.END}\n")

# [✅]
def send_email(file_path):
    '''
    Sends the specified file via email.
    '''

    # Getting the email for the sender
    SENDER_EMAIL = input("Enter the email of the sender: ")
    # Getting the email for the reciever
    RECIPIENT_EMAIL = input("Enter the email of the reciever: ")

    # Google generated password, getting the sender_email is just extra security
    # This is a throwaway email
    SENDER_PASSWORD = 'zkgz avdi irab hwjg'

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = 'Dream Journal Backup'

    body = 'Please find the attached backup of the dream journal.'
    msg.attach(MIMEText(body, 'plain'))

    attachment = open(file_path, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
    msg.attach(part)
    attachment.close()

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print(f'\n{Color.GREEN}Email sent successfully!{Color.END}\n')
    except Exception as e:
        print(f'\n{Color.RED}Failed to send email: {e}{Color.END}\n')

# [❌]
def statistics():
    return None

# [✅]
def log(event, details):
    '''
    A function to create a log event
    '''

    # Getting the formatted date
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Opening the logs file
    with open(LOGS_FILE, 'a') as log:
        # Writing to our file in a formatted manner
        log.write(f"\n[{timestamp}] | {event}: {details}\n")

# [✅]
def get_logs():
    '''
    A function that prints the logs to screen
    '''

    print(f"\n{Color.GREEN}Getting Logs{Color.END}")
    with open(LOGS_FILE, 'r') as file:
        content = file.read()
        print(content)

# [✅]
def clear_logs():
    '''
    A function that clears the logs.txt file
    '''

    print(f"\n{Color.GREEN}Clearing Logs{Color.END}\n")
    try:
        with open(LOGS_FILE, 'w') as f:
            f.truncate(0)  # Truncate the file to size 0
        print(f"{Color.GREEN}Successfully cleared the logs file: {LOGS_FILE}{Color.END}\n")
    except Exception as e:
        print(f"{Color.RED}Error clearing the logs file: {e}{Color.END}")

# [✅]
def get_template():
    '''
    A fuinction that opens the template using the text editor
    '''
    print(f"\n{Color.GREEN}Opening Journal Template{Color.END}\n")
    subprocess.run(TEXT_EDITOR + [TEMPLATE_DIRECTORY])
    
# [✅]
def display_help():
    '''
    A function that displays all commands
    '''

    print(f"\nAvailable commands: \n")
    print(f"'{Color.GREEN}create{Color.END}'       - Create a new journy entry")
    print(f"'{Color.GREEN}navigate{Color.END}'     - View yur dream entries")
    print(f"'{Color.GREEN}stats{Color.END}'        - View your dream statistics\n")
    print(f"'{Color.GREEN}backup{Color.END}'       - Back up all exisiting dreams to a (.txt)")
    print(f"'{Color.GREEN}sync{Color.END}'         - Sync all your dreams from a backup file (.txt)\n")
    print(f"'{Color.GREEN}logs{Color.END}'         - Check the programs logs")
    print(f"'{Color.GREEN}clr_logs{Color.END}'     - Clear the programs logs")
    print(f"'{Color.GREEN}clear{Color.END}'        - Clear the terminal")
    print(f"'{Color.GREEN}exit{Color.END}'         - Exit the program\n")

# [✅]
def clear_terminal():
    ''' 
    A function that clears the terminal using 'clear' command
    '''

    os.system('cls' if os.name == 'nt' else 'clear')
    print(PROGRAM_NAME)

# [✅]
def handle_commands(input_command):
    '''
    A function that connects all commands to their functions
    '''

    commands = {
        "help": display_help,
        "create": create_entry,
        "navigate": navigate,

        "sync": sync,
        "backup": backup,

        "logs": get_logs,
        "clr_logs": clear_logs,
        "template": get_template,
        "clear": clear_terminal,

        "exit": exit  # Assuming you want to exit the program
    }

    command_func = commands.get(input_command)
    if command_func:
        command_func()
    else:
        print(f"\n{Color.RED}Unknown Command{Color.END}: [{input_command}] | Type 'help' for a list of commands.\n")

# [✅]
def main():
    '''
    A function that creates the program loop,
    it only exits if the user enters the exit command
    '''

    clear_terminal() 
    while True:
        user_command = input("Enter a command (type 'help' for commands): ").strip().lower()
        handle_commands(user_command)

# [✅]
def loader():
    '''
    A function that ensures that all directories have been made,
    and are in the proper location / exists

    Returns:
        True if everything is in the right location, False otherwise
    '''

    # We must check if we have valid directories
    DIRECTORIES = [
        JOURNAL_DIRECTORY,
        BACKUP_DIRECTORY,
    ]

    # Let's loop through our directories
    for dir in DIRECTORIES:
        # Check if this directory does not exist
        if not os.path.isdir(dir):
            return False
    
    # Otherwise, return True
    return True

#
if __name__ == "__main__":
    loaded = loader()
    if loaded:
        main()
    else:
        print(f"\n{Color.RED}Invalid Directories!\n1. Go Inside dream-journal/src/journal.py\n2. Go To The Top Of The File\n3. Swap Directory Variables With Valid Directories\n4. Rerun Program{Color.END}") 