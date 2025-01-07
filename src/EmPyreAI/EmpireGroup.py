# This file contains the EmpireGroup class to represent a group of users on the Empire AI Alpha system.
#
# Class Properties:
#   - id = (get) Returns the GID number
#   - name = (get) Returns the name of the groups
#   - members = (get) Returns a list of usernames with membership in this group
#
# Static Functions:
#   - Exists(): Returns bool. True if the group exists, False if it does not.
#
# Class Functions:
#   - GetFromCMD(): Loads group data from the Base Command API into the group_data variable. Returns (bool)
#   - Commit(): Commits changes of group information to the Base Command API. Returns (bool).
#   - AddMember(): Adds a member to the membership list of this group. Returns (bool).
#   - RemoveMember(): Removes a member from the membership list of this group. Returns (bool).
#  
# This makes use of the EmPyreAI module and ultimately the Base Command API
#   to provide user management capabilities to coordinators without requiring
#   elevated privileges on the cluster.
#
# Author: Kali McLennan (Flatiron Institute) - kmclennan@flatironinstitute.org

import os
import pwd
import EmPyreAI.EmpireAPI
from pythoncm.entity import User
import getpass
import json
import EmPyreAI.EmpireUtils as EUtils
import re
from datetime import datetime
import sys
import grp
import pwd

class EmpireGroup:
  #region Constructors
  def __init__(self, groupname):
    """Initialize an EmpireGroup instance for the specified group."""
    self.exists = False
    self.GetFromCMD(groupname)
  #endregion 

  #region Static Methods
  @staticmethod
  def Exists(groupname):
    group_data = EmPyreAI.EmpireAPI.CMSH_Cluster.get_by_name(groupname, 'Group')
    EmPyreAI.EmpireAPI.CMSH_Cluster.disconnect()
    if group_data == None:
      return False
    return True
  #endregion

  #region Instance Methods
  def GetFromCMD(self, groupname):
    # We need to make sure that anyone attempting to modify these groups is a member of them
    user_groups = [g.gr_name for g in grp.getgrall() if getpass.getuser() in g.gr_mem]
    gid = pwd.getpwnam(getpass.getuser()).pw_gid
    user_groups.append(grp.getgrgid(gid).gr_name)
    
    self.group_data = EmPyreAI.EmpireAPI.CMSH_Cluster.get_by_name(groupname, 'Group')
    if self.group_data == None:
      self.exists = False
      return False
    else:
      self.exists = True

  def CanChange(self, username):
    # Automatically reject any changes to the sudo group
    if self.name == "sudo":
      return False

    # Get a list of groups that the current user is in
    user_groups = [g.gr_name for g in grp.getgrall() if getpass.getuser() in g.gr_mem]
    gid = pwd.getpwnam(getpass.getuser()).pw_gid
    user_groups.append(grp.getgrgid(gid).gr_name)

    if self.name not in user_groups:
      return False
    return True

  def Commit(self):
    """Commit changes to Base Command"""
    if self.CanChange(getpass.getuser()) == False: 
      print(f"[ \033[31mERROR\033[0m ] You are not allowed to modify membership of the group \033[31m{self.name}\033[0m.")
      sys.exit(1)
    result = self.group_data.commit()
    if result.good:
      return True
    else:
      return False
    
  def AddMember(self, username, force=False):
    if force == False:
      if EUtils.PromptConfirm(f"Add user \033[32m{username}\033[0m to the group \033[32m{self.name}\033[0m? (Y/N)"):
        self.group_data.members.append(username)
        return self.Commit()
    else:
      self.group_data.members.append(username)
      return self.Commit()
    return False


  def RemoveMember(self, username, force=False):
    if force == False:
      if EUtils.PromptConfirm(f"Remove user \033[31m{username}\033[0m to the group \033[31m{self.name}\033[0m? (Y/N)"):
        self.group_data.members.remove(username)
        return self.Commit()
    else:
      self.group_data.members.remove(username)
      return self.Commit()
    return False
  #endregion

  #region Getters, Setters, and property definitions

  #region Group GID Property
  def GetGID(self):
    return self.group_data.ID
  
  id = property(GetGID)
  #endregion

  #region Group Name Property
  def GetName(self):
    return self.group_data.name
  
  name = property(GetName)
  #endregion

  #region Group Member Properties
  def GetMembers(self):
    return self.group_data.members

  members = property(GetMembers)
  #endregion
  