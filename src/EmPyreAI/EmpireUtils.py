import getpass
import os
import random

def GenPassword(length=14):
    """Generate a random string of alphanumeric characters with a few exceptions to prevent confusion."""
    allowed_characters = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789"
    return ''.join(random.choices(allowed_characters, k=length))
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
    
