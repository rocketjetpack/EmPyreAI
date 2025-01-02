import getpass
import os
import random
import sys
import re

MinimumUsernameLength = 4

def FormatPhoneNumber(phone):
    # Remove non-digit characters
    digits = ''.join(filter(str.isdigit, phone))

    # Check if the number has at least 10 digits (to include local and country code)
    if len(digits) < 10:
        return False, phone

    # Separate country code if the number is longer than 10 digits
    if len(digits) > 10:
        country_code = digits[:-10]
        local_number = digits[-10:]
        formatted_number = f"+{country_code} {local_number[:3]}-{local_number[3:6]}-{local_number[6:]}"
    else:
        formatted_number = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"

    return True, formatted_number

def GenPassword(length=14):
    """Generate a random string of alphanumeric characters with a few exceptions to prevent confusion."""
    allowed_characters = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789"
    return ''.join(random.choices(allowed_characters, k=length))

def Success(message):
    print(f"[\033[32m SUCCESS\033[0m ] {message}")

def Warning(message):
    print(f"[\033[93m WARNING\033[0m ] {message}")

def Error(message, fatal: bool = False, exit_code: int = 1):
    print(f"[\033[31m ERROR\033[0m ] {message}")
    if fatal:
      sys.exit(exit_code)

def PromptConfirm(message=None):
    if message != None:
        print(message)
    while True:
        response = input("Please enter yes or no: ").lower()
        if response in ("yes", "y"):
            return True
        elif response in ("no", "n"):
            return False
        else:
            print("Invalid input. Please enter yes or no.")

def CheckAPI():
    """This utility function verifies that the required API access keys are present."""
    username = getpass.getuser()
    if username == "root":
        return True
    
    # Confirm that the required certificate files exist
    if os.path.exists(f"/mnt/home/{username}/.empireai/cmsh_api.key"):
        if os.path.exists(f"/mnt/home/{username}/.empireai/cmsh_api.pem"):
            return True
        else:
            print(f"The users certificate key file does not exist at /mnt/home/{username}/.empireai/cmsh_api.key")   
    else:
        print(f"The users certificate key file does not exist at /mnt/home/{username}/.empireai/cmsh_api.key")
    
    return False
