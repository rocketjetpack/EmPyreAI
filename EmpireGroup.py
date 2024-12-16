import os
import pwd
from pythoncm.cluster import Cluster
from pythoncm.settings import Settings
from pythoncm.entity import User
import getpass
import json
import EmPyreAI.EmpireUtils as EUtils
import re
from datetime import datetime
import sys

class EmpireGroup:
  #region Constructors
  def __init__(self, groupname):
    """Initialize an EmpireGroup instance for the specified group."""
    if getpass.getuser() == "root":
      self.cluster = Cluster()
    else:
      self.cmd_settings = Settings(
        host="alpha-mgr",
        port=8081,
        cert_file=f'/mnt/home/{getpass.getuser()}/.empireai/cmsh_api.pem',
        key_file=f'/mnt/home/{getpass.getuser()}/.empireai/cmsh_api.key',
        ca_file='/usr/lib64/python3.9/site-packages/pythoncm/etc/cacert.pem'
      )
      self.cluster = Cluster(self.cmd_settings)
    self.exists = False
    self.GetFromCMD(groupname)
  #endregion 

  #region Static Methods
  @staticmethod
  def Exists(groupname):
    cmd_settings = Settings(
      host="alpha-mgr",
      port=8081,
      cert_file=f'/mnt/home/{getpass.getuser()}/.empireai/cmsh_api.pem',
      key_file=f'/mnt/home/{getpass.getuser()}/.empireai/cmsh_api.key',
      ca_file='/usr/lib64/python3.9/site-packages/pythoncm/etc/cacert.pem'
    )
    cluster = Cluster(cmd_settings)
    group_data = cluster.get_by_name(groupname, 'Group')
    cluster.disconnect()
    if group_data == None:
      return False
    
    return True
  #endregion

  #region Instance Methods
  def GetFromCMD(self, groupname):
    if groupname == "sudo" or groupname == "coordinator":
      print(f"[ \033[31mERROR\033[0m ] You are not allowed to modify membership of the group \033[31m{groupname}\033[0m.")
      sys.exit(1)
    
    self.group_data = self.cluster.get_by_name(groupname, 'Group')
    if self.group_data == None:
      self.exists = False
      return False
    else:
      self.exists = True

  def Commit(self):
    """Commit changes to Base Command"""

    if self.name == "sudo" or self.name == "coordinator":
      print(f"[ \033[31mERROR\033[0m ] You are not allowed to modify membership of the group \033[31m{self.name}\033[0m.")
      sys.exit(1)
    result = self.group_data.commit()
    if result.good:
      return True
    else:
      return False
    
  def AddMember(self, username, force=False):
    if force == False:
      if EUtils.PromptConfirm(f"Add user \033[32m{username}\033[0m from the group \033[32m{self.name}\033[0m? (Y/N)"):
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
