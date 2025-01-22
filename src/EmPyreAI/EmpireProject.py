# This file contains the EmpireProject class to represent a research project on the Empire AI Alpha system.
#
# Projects are owned by a Principal Investigator (PI) entity and non-PI users can be associated with the project
# for accounting purposes.
#
# Project Data Structure:
#   Properties:
#     - Institution
#     - Title (long)
#     - Title (short)
#     - Principal Investigator (Name)
#     - Location (Physical location)
#     - Department
#     - ID Number (Auto increment)
# 
# This data will be used to generate a list of EmpireProject objects, each representing one reserach project
#   and ultimately saved via pickle to a file on the head node.
#
# This makes use of the EmPyreAI module and ultimately the Base Command API
#   to provide user management capabilities to coordinators without requiring
#   elevated privileges on the cluster.
#
# Author: Kali McLennan (Flatiron Institute) - kmclennan@flatironinstitute.org

import os
import pickle
import EmpireUtils as E_Utils

class EmpireProjectList:
    def __init__(self):
        self.LoadProjects()

    def LoadProjects(self):
        filePath = "/opt/EmpireAI-Tools/share/projects.bin"
        if os.path.exists(filePath):
            with open(filePath, "rb") as file:
                try:
                    self.Projects = pickle.load(file)
                    return True
                except pickle.UnpicklingError as e:
                    E_Utils.Error(f"(pickle error) Failed to load project data from {filePath}!")
                    self.Projects = None
                    return False
                except Exception as e:
                    E_Utils.Error(f"Unhandled exception while attempting to load project data from {filePath}")
                    E_Utils.Error(e)
                    self.Projects = None
                    return False
        else:
            E_Utils.Warning(f"No file found at {filePath} to load project data from. Instantiating an empty list.")
            self.Projects = list()
            return True

    def Save(self):
        filePath = "/opt/EmpireAI-Tools/share/projects.bin"
        try:
            os.makedirs(os.path.dirname(filePath), exist_ok=True)
            with open(filePath, 'wb') as file:
                pickle.dump(self.Projects, file)
                E_Utils.Success("Project data has been saved.")
                return True
        except pickle.PicklingError as e:
            E_Utils.Error(f"(pickle error) Failed to save project data to {filePath}!")
            E_Utils.Error(e)
        except Exception as e:
            E_Utils.Error(f"Unhandled exception while attempting to save project data to {filePath}!")
        return False

class EmpireProject:
#region Static Methods
    @staticmethod
    def New(institution, titleLong, titleShort, pi_name, location, department):
        project = EmpireProject()
        project.Institution = institution
        project.LongTitle = titleLong
        project.Title = titleShort
        project.PI = pi_name
        project.Location = location
        project.Department = department
        project.ID = EmpireProject.GetNextID()
        return project
#endregion

#region Class Methods
#endregion

#region Properties
    def GetInstitution(self):
        return self._institution
    
    def SetInstitution(self, value):
        if value not in ["cornell", "nyu", "suny", "cuny", "rpi", "columbia"]:
            print("EmpireProject: Attempt to set the institution of a project to an invalid value.")
        else:
            self._institution = value
    
    Institution = property(GetInstitution, SetInstitution)

    def GetLongTitle(self):
        return self._long_title
    
    def SetLongTitle(self, value):
        self._long_title = value

    LongTitle = property(GetLongTitle, SetLongTitle)

    def GetShortTitle(self):
        return self._title
    
    def SetShortTitle(self, value):
        self._title = value

    Title = property(GetShortTitle, SetShortTitle)

    def GetPI(self):
        return self._pi
    
    def SetPI(self, value):
        self._pi = value
    
    PI = property(GetPI, SetPI)

    def GetLocation(self):
        return self._location
    
    def SetLocation(self, value):
        self._location = value

    Location = property(GetLocation, SetLocation)

    def GetDepartment(self):
        return self._department
    
    def SetDepartment(self, value):
        self._department = value

    Department = property(GetDepartment, SetDepartment)

    def GetID(self):
        return self._id

    ID = property(GetID)
#endregion