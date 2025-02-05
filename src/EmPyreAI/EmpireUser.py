# This file contains the EmpireUser class to represent a group of users on the Empire AI Alpha system.
#
# Class Properties:
#   - username = (get) Returns the username of the account
#   - firstname = (get|set) Returns or sets the first name of the account
#   - lastname = (get|set) Returns or sets the last name of the account
#   - notes = (get|set) Returns or sets the notes about the user as a Python dictionary
#   - phone = (get|set) Returns or sets the "phone" key of the notes field
#   - email = (get|set) Returns or sets the email of the account
#   - project = (get|set) Returns or sets the "project" key of the notes field
#   - uid = (get) Returns the UID of the user
#   - groups = (get|set) Returns or sets a list of EmpireGroup objects representing POSIX group membership
#
# Notes:
#   When the notes property is interacted with it should detect absent or malformed notes
#   and attempt to correct the format of the notes or generate a new minimal-content
#   set of notes. Users created early in the Alpha system do not have PI affiliation,
#   project affiliation, and some have no notes at all.
#
# Static Functions:
#   - Exists(): Returns bool. True if the user exists, False if it does not.
#
# Class Functions:
#   - GetFromCMD(): Loads user data from the Base Command API into the user_data variable. Returns (bool)
#   - Commit(): Commits changes of user information to the Base Command API. Returns (bool).
#   - SetUserData(): Accepts a dictionary and makes a bulk commit to Base Command without confirmation. Returns (bool).
#   - AppendNote(): Adds a new key to the notes property. Returns (bool).
#  
# This makes use of the EmPyreAI module and ultimately the Base Command API
#   to provide user management capabilities to coordinators without requiring
#   elevated privileges on the cluster.
#
# Author: Kali McLennan (Flatiron Institute) - kmclennan@flatironinstitute.org

import EmPyreAI.EmpireAPI as E_API
import EmPyreAI.EmpireUtils as E_Utils
from pythoncm.entity import User
import getpass
from datetime import datetime
import json
import re

class EmpireUser:
    @staticmethod
    def Exists(username: str):
        """Use the pythoncm API (represented as EmPyreAI.EmpireAPI/E_API) to determine if there is a User object
        matching the supplied username.
        Input:
          - username: string
        Return:
          - True if the user exists
          - False if the user does not exist
        """
        user_data = E_API.CMSH_Cluster.get_by_name(username, 'User') # Ask BaseCommand for the User object with the supplied username
        if user_data == None:
            return False
        return True

#region Static Methods
    @staticmethod
    def New(username: str):
        retVal = User(E_API.CMSH_Cluster)
        retVal.name = username
        retVal.password = E_Utils.GenPassword(28)
        retVal.homeDirectory = f"/mnt/home/{username}"
        retVal.loginShell = "/bin/bash"
        creationTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        retVal.notes = f'{ "created_by": "{getpass.getuser()}", "created_at": "{creationTime}"}'
        return retVal
    
    def GetAll():
        retVal = list()
        print(E_API.CMSH_Cluster.entities)
#endregion

#region Constructor
    def __init__(self, username: str):
        if EmpireUser.Exists(username) == True:
            self.UserData = E_API.CMSH_Cluster.get_by_name(username, 'User')
            self.Committed = True
        else:
            E_Utils.Warning(f"A request was made to load user data from CMSH for username {username} but this user does not exist. Creating a new user.")
            self.UserData = User(E_API.CMSH_Cluster)
            self.UserData.name = username
            self.UserData.homeDirectory = f"/mnt/home/{username}"
            self.UserData.loginShell = "/bin/bash"
            creationData = {}
            creationData["created_by"] = getpass.getuser()
            creationData["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.UserData.notes = json.dumps(creationData)
            self.Committed = False     
#endregion

#region Class Methods
    def Commit(self, force: bool = False):
        """Commit any pending changes to this object via the pythoncm API.
        Input:
          - None
        Return:
          - True if the commit is successful
          - False if it is unsuccessful
        """
        if self.Committed == True and force == False:
            E_Utils.Warning(f"Commit called on user named {self.Username} but no modifications have been made that require committing.")
            return True
        
        if self.UserData.commonName == None or len(self.UserData.commonName) == 0:
            E_Utils.Error(f"Attempting to commit a user object that has no commonName defined. Aborting!")
            return False
        
        if self.UserData.surname == None or len(self.UserData.surname) == 0:
            E_Utils.Error(f"Attempting to commit a user object that has no surname defined. Aborting!")
            return False
        
        if self.UserData.email == None or len(self.UserData.email) == 0:
            E_Utils.Error(f"Attempting to commit a user object that has no email defined. Aborting!")
            return False
        
        notes = self.Notes
        notes["last_modified_by"] = getpass.getuser() # Store who committed the last change to this object
        notes["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Store the current time as the last modification time
        self.Notes = notes
        result = self.UserData.commit()
        if result.good:
            self.Committed = True
            return True
        return False
    
    def RandomizePassword(self, length: int = 14):
        """Generate a new password for this user.
        Input:
          - length: integer representing how long the generated password should be
        Return:
          - str: the plain-text generated password if the Commit() call succeeds
          - None: if the Commit() call fails
        """
        new_password = E_Utils.GenPassword(length)
        self.UserData.password = new_password
        if self.Commit():
            return new_password
        return None
    
    def SetNote(self, key: str, value: str):
        """Set the value of a particular note.
        Input:
          - key: str representing the name of the note
          - value: str representing the value of the note
        Return:
          - None
        """
        notes = self.Notes
        notes[key] = value
        self.Notes = notes

    def SendWelcomeEmail(self):
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        import jinja2

        environment = jinja2.Environment(loader=jinja2.FileSystemLoader("/opt/EmpireAI-Tools/templates"))
        template = environment.get_template("new_user_email.template")
        content = template.render(firstname=self.FirstName, username=self.Username, institution=self.Institution)
        smtp_server = "alpha-mgr"
        smtp_port = 25
        from_email = "help@empire-ai.org"
        to_email = self.Email
        subject = "Empire AI Alpha Account Creation Notice"

        message = MIMEMultipart("alternative")
        message["From"] = from_email
        message["To"] = to_email
        message["Subject"] = subject
        mime_text = MIMEText(content, "html")
        message.attach(mime_text)
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.sendmail(from_email, to_email, message.as_string())
            print(f"[\033[32m SUCCESS\033[0m ] Sent a welcome email to {self.Email}.")
        except Exception as e:
            print(f"[\033[31m ERROR\033[0m ] Failed to send a welcome email to {self.Email}. Error details: {e}.")
#endregion 

#region Class Properties (Getters and Setters)
    def GetPhone(self):
        notes = self.Notes
        if "phone" in notes.keys():
            return notes["phone"]
        return None
    
    def SetPhone(self, value):
        self.SetNote("phone", value)
        self.Committed = False
    
    Phone = property(GetPhone, SetPhone)

    def GetLab(self):
        notes = self.Notes
        if "lab" in notes.keys():
            return notes["lab"]
        return None
    
    def SetLab(self, value):
        self.SetNote("lab", value)
        self.Committed = False

    Lab = property(GetLab, SetLab)

    def GetInstitution(self):
        notes = self.Notes
        if "institution" in notes.keys():
            return notes["institution"]
        return None
    
    def SetInstitution(self, value):
        self.SetNote("institution", value)
        self.Committed = False

    Institution = property(GetInstitution, SetInstitution)

    def GetPI(self):
        notes = self.notes
        if "pi" in notes.keys():
            return notes["pi"]
        return None
    
    def SetPI(self, value):
        self.SetNote("pi", value)
        self.Committed = False

    PI = property(GetPI, SetPI)

    def GetUID(self):
        return self.UserData.ID
    
    ID = property(GetUID)

    def GetUsername(self):
        return self.UserData.name
    
    Username = property(GetUsername)

    def GetFirstname(self):
        return self.UserData.commonName
    
    def SetFirstname(self, value):
        self.UserData.commonName = value
        self.Committed = False

    FirstName = property(GetFirstname, SetFirstname)

    def GetLastname(self):
        return self.UserData.surname
    
    def SetLastname(self, value):
        self.UserData.surname = value
        self.Committed = False
    
    LastName = property(GetLastname, SetLastname)

    def GetFullname(self):
        return f"{self.FirstName} {self.LastName}"
    
    FullName = property(GetFullname)

    def GetEmail(self):
        return self.UserData.email
    
    def SetEmail(self, value):
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if (re.fullmatch(email_regex, value)):
            self.UserData.email = value
            self.Committed = False
        else:
            E_Utils.Error(f"Attempted to set an invalid email address ({value}) for user {self.UserData.name}. Aborting.")

    Email = property(GetEmail, SetEmail)

    def GetGroups(self):
        import grp, pwd
        retVal = [g.gr_name for g in grp.getgrall() if self.Username in g.gr_mem]
        gid = pwd.getpwnam(self.Username).pw_gid
        retVal.append(grp.getgrgid(gid).gr_name)
        return retVal
    
    Groups = property(GetGroups)

    def GetNotes(self):
        """Convert the User.notes field from pythoncm form JSON to a Python dict object and return it."""
        if self.UserData.notes != None and len(self.UserData.notes) > 0:
            try:
                return json.loads(self.UserData.notes) # Attempt to decode the UserData.notes field from JSON to a dict and return it           
            except Exception as e:
                # If unable to decode UserData.notes as JSON then create a new dict and set the 'other' key to the existing notes for this user.
                E_Utils.Error(f"Unable to decode notes for the user {self.username}. Adding any existing notes as the 'other' key and returning a valid data structure.")
                userNotes = {}
                userNotes["other"] = self.UserData.notes
                self.UserData.notes = json.dumps(userNotes)
                self.Commtted = False
                return userNotes
        else:
            self.UserData.notes = "{}"
            self.Committed = False
            return {} # Return an empty dict

    def SetNotes(self, notesDict):
        try:
            self.UserData.notes = json.dumps(notesDict)
            self.Committed = False
        except Exception as e:
            E_Utils.Error("Failed to encode notes value as a JSON string. Recovering existing note data in the 'other' key.")
            newNotes = {}
            newNotes["other"] = str(notesDict)
            self.UserData.notes = json.dumps(newNotes)
            self.Committed = False
    
    
    Notes = property(GetNotes, SetNotes)

    def GetHomeDirectory(self):
        return self.UserData.homeDirectory
    
    def SetHomeDirectory(self, value):
        self.UserData.homeDirectory = value
        self.Committed = False

    HomeDirectory = property(GetHomeDirectory, SetHomeDirectory)

    def GetShell(self):
        return self.UserData.loginShell
    
    def SetShell(self, value):
        self.UserData.loginShell = value
        self.Committed = False
    
    Shell = property(GetShell, SetShell)

    def GetLastModified(self):
        if "last_modified" in self.Notes.keys() and "last_modified_by" in self.Notes.keys():
            retVal = {}
            retVal["date"] = self.Notes["last_modified"]
            retVal["by"] = self.Notes["last_modified_by"]
            return retVal
        else:
            E_Utils.Warning("Last modification information is missing. Populating it now.")
            self.SetNote(key="last_modified", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.SetNote(key="last_modified_by", value=getpass.getuser())
            self.Committed = False
            retVal = {}
            retVal["date"] = self.Notes["last_modified"]
            retVal["by"] = self.Notes["last_modified_by"]
            return retVal
        
    LastModified = property(GetLastModified)

    def GetCreation(self):
        if "created_at" in self.Notes.keys() and "created_by" in self.Notes.keys():
            retVal = {}
            retVal["date"] = self.Notes["created_at"]
            retVal["by"] = self.Notes["created_by"]
            return retVal
        else:
            E_Utils.Warning("Creation information is missing. Populating it now.")
            self.SetNote(key="created_at", value="2024-01-01 00:00:00")
            self.SetNote(key="created_by", value="unknown")
            self.Committed = False
            retVal = {}
            retVal["date"] = self.Notes["created_at"]
            retVal["by"] = self.Notes["created_by"]
            return retVal
            
    Creation = property(GetCreation)

#endregion