# This file contains the EmpireCoordinator class to represent a coordinator account on the Empire AI Alpha system.
#
# Coordinators have elevated access to the Empire AI Alpha system through various mechanisms. The primary means of
# elevated access are through the Nvidia Base Command `pythoncm` API and through assignment as Account Coordinators
# in Slurm.
#
# Class Properties:
#   - user = (get) Returns an EmpireUser instance representing this user
#
# Class Functions:
#   - EnableCoordinator(): Set the is_coordinator note for the EmpireUser instance and add group membership
#   - DisableCoordinator(): Set the is_coordinator note for the EmpireUser instance and remove group membership
#
# This makes use of the EmPyreAI module and ultimately the Base Command API
#   to provide user management capabilities to coordinators without requiring
#   elevated privileges on the cluster.
#
# Author: Kali McLennan (Flatiron Institute) - kmclennan@flatironinstitute.org

from EmPyreAI.EmpireUser import EmpireUser
import EmPyreAI.EmpireUtils as EUtils

class EmpireCoordinator:
    def __init__(self, username):
        if EmpireUser.Exists(username):
            self.user = EmpireUser(username)
            if "is_coordinator" in self.user.notes.keys():
                self.is_coordinator = self.user.notes["is_coordinator"]
            else:
                self.is_coordinator = False
        else:
            return False
        
    def EnableCoordinator(self):
        """This function will flag this account as a coordinator and add them to the necessary LDAP group."""
        self.user.AppendNote("is_coordinator", "True")
        self.user.Commit()
        # Refresh our cached data
        self.is_coordinator = True
        
    def DisableCoordinator(self):
        """This function will remove the coordinator note and remove them from the LDAP group."""
        notes = self.user.notes
        notes["is_coordinator"] = "False"
        self.user.notes = notes
        self.user.Commit()
        # Refresh our cached data
        self.is_coordinator = False
    
