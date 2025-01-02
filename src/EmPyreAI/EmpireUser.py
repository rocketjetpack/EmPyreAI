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
#
# Static Functions:
#   - Exists(): Returns bool. True if the user exists, False if it does not.
#   - New(): Returns bool. Creates a new stub user in Base Command.
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

import os
import pwd
#from pythoncm.cluster import Cluster
#from pythoncm.settings import Settings
import EmPyreAI.EmpireAPI
from pythoncm.entity import User
import getpass
import json
import EmPyreAI.EmpireUtils as EUtils
import EmPyreAI.EmpireAPI
from EmPyreAI.EmpireGroup import EmpireGroup
from EmPyreAI.EmpireSlurm import EmpireSlurm
import re
from datetime import datetime
import grp
import sys
import pwd
import jinja2

class EmpireUser:
  #region Constructors
  def __init__(self, username, load=True):
    """Initialize an EmpireUser instance for the specified username."""
    if load:
      self.GetFromCMD(username)
  #endregion 

  #region Static Methods
  @staticmethod
  def Exists(username):
    user_data = EmPyreAI.EmpireAPI.CMSH_Cluster.get_by_name(username, 'User')
    #EmPyreAI.EmpireAPI.CMSH_Cluster.disconnect()
    if user_data == None:
      return False
    return True

  def Add(self, userData):
    self.user_data = EmPyreAI.EmpireAPI.CMSH_Cluster.get_by_name(userData['username'], 'User')
    if self.user_data != None:
      return False
    
    self.user_data = User(EmPyreAI.EmpireAPI.CMSH_Cluster)
    self.user_data.name = userData["username"]
    self.user_data.password = EUtils.GenPassword()
    self.user_data.email = userData["email"]
    self.user_data.homeDirectory = f"/mnt/home/{userData['username']}"
    self.user_data.commonName = userData["commonName"]
    self.user_data.surname = userData["surname"]
    self.user_data.notes = '{ "created_by": "' + getpass.getuser() + '", "created_at": "' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '" }'

    commit_result = self.Commit()
    return commit_result      
  
  @staticmethod
  def FetchAllUsers():
    print(json.dumps(EmPyreAI.EmpireAPI.CMSH_Cluster.get_user_data()))
  #endregion

  #region Instance Methods
  def SendWelcomeEmail(self):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    environment = jinja2.Environment(loader=jinja2.FileSystemLoader("/opt/EmpireAI-Tools/templates"))
    template = environment.get_template("new_user_email.template")
    content = template.render(firstname=self.firstname, username=self.username, institution=self.institution)
    smtp_server = "alpha-mgr"
    smtp_port = 25
    from_email = "help@empire-ai.org"
    to_email = self.email
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
        print(f"[\033[32m SUCCESS\033[0m ] Sent a welcome email to {self.email}.")
    except Exception as e:
        print(f"[\033[31m ERROR\033[0m ] Failed to send a welcome email to {self.email}. Error details: {e}.")

  def LoadFromJSON(self, jsonData):
    self.user_data = jsonData

  def AddToGroup(self, groupname, force=False):
    group = EmpireGroup(groupname)
    return group.AddMember(self.username, force=force)

  def RandomizePassword(self, length=14):
    new_password = EUtils.GenPassword(length)
    self.user_data.password = new_password
    if self.Commit():
      return new_password
    else:
      return None

  def SetUserData(self, data):
    """Commit a set of new user data without prompting for each change."""
    # data should be a list of key=>value entries conforming to the expected values of Base Command
    for key, value in data.items():
      self.user_data[f"{key}"] = value

    if not self.Commit():
      return False
    
    return True

  def GetFromCMD(self, username):
    self.user_data = EmPyreAI.EmpireAPI.CMSH_Cluster.get_by_name(username, 'User')
    if self.user_data == None:
      self.exists = False
      return False
    else:
      self.exists = True


  def Commit(self):
    """Commit changes to Base Command"""
    notes = self.notes
    notes["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    notes["last_modified_by"] = getpass.getuser()
    self.notes = notes
    result = self.user_data.commit()
    if result.good:
      return True
    else:
      return False
    
  def AppendNote(self, key, value):
    """Add a new field to the notes for this user."""
    notes = self.notes
    notes[key] = value
    self.notes = notes
    result = self.Commit()

    return result
  #endregion

  #region Getters, Setters, and property definitions
  def GetPhone(self):
    if self.notes["phone"] != None:
      return self.notes["phone"]
    else:
      return None
    
  def GetProject(self):
    if self.notes["project"] != None:
      return self.notes["project"]
    else:
      return None
  
  #region Institution Property
  def GetInstitution(self):
    if self.notes["institution"] != None:
      return self.notes["institution"]
    else:
      return None
    
  institution = property(GetInstitution)
  #endregion

  #region PI Property
  def GetPI(self):
    if "pi" in self.notes:
      return self.notes["pi"]
  
  def SetPI(self, value):
    if "pi" in self.notes:
      self.notes["pi"] = value
      self.Commit()
    else:
      self.AppendNote("pi", value)
      self.Commit()

  pi = property(GetPI, SetPI)
  #endregion

  #region Username Property
  def GetUsername(self):
    return self.user_data.name
  
  username = property(GetUsername)
  #endregion
  
  #region First and Last Name Properties
  def GetFirstName(self):
    return self.user_data.commonName
  
  def SetFirstname(self, value):
    if EUtils.PromptConfirm(f"Commit change of firstname from {self.user_data.commonName} to {value}? (Y/N)"):
      self.user_data.commonName = value
      self.Commit()
    else:
      print("Aborting change of first name.")
  
  def GetLastName(self):
    return self.user_data.surname
  
  def SetLastName(self, value):
    if EUtils.PromptConfirm(f"Commit change of lastname from {self.user_data.surname} to {value}? (Y/N)"):
      self.user_data.surname = value
    else:
      print("Aborting change of last name.")

  lastname = property(GetLastName, SetLastName)
  firstname = property(GetFirstName, SetFirstname)
  #endregion 

  #region Notes Properties
  def GetNotes(self):
    if len(self.user_data.notes) == 0:
      return {}

    try:
      retVal = json.loads(self.user_data.notes)    
      return retVal
    except:
      return False

  
  def SetNotes(self, value):
    try:
      self.user_data.notes = json.dumps(value)
    except:
      notes = {}
      notes["other"] = value
      self.user_data.notes = json.dumps(notes)

  notes = property(GetNotes, SetNotes)
  #endregion

  #region Phone Property
  def GetPhone(self):
    try:
      return self.notes["phone"]
    except:
      return None
  
  def SetPhone(self, value):
    if EUtils.PromptConfirm(f"Commit change of phone number to {value} for user {self.user_data.name}? (Y/N)"):
      try:
        data = self.notes
        data["phone"] = value
        self.notes = data
        self.Commit()
      except:
        print(f"Failed to set a phone number for {self.user_data.name}")
    else:
      print("User cancelled the request.")

  phone = property(GetPhone, SetPhone)
  #endregion

  #region Email Property
  def GetEmail(self):
    return self.user_data.email
  
  def SetEmail(self, value):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if (re.fullmatch(email_regex, value)):
      if EUtils.PromptConfirm(f"Commit change of email to {value} for user {self.user_data.name}? (Y/N)"):
        self.user_data.email = value
        self.Commit()
      else:
        print("User cancelled the request.")
    else:
      print(f"{value} is not a valid email address. Aborting.")

  email = property(GetEmail, SetEmail)
  project = property(GetProject)
  #endregion
  
  #region Groups Property
  def GetGroups(self):
    # use pwd and grp modules as they are SIGNIFICANTLY faster than looping objects in pythoncm
    self.groups = [g.gr_name for g in grp.getgrall() if self.username in g.gr_mem]
    gid = pwd.getpwnam(self.username).pw_gid
    self.groups.append(grp.getgrgid(gid).gr_name)
    return self.groups
  
  groups = property(GetGroups)
  #endregion