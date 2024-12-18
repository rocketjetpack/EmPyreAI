# This file contains the EmpireSlurm class to represent a group of users on the Empire AI Alpha system.
#
# Class Properties (readonly):
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
# API Documentation: https://slurm.schedmd.com/rest_api.html
#
# Author: Kali McLennan (Flatiron Institute) - kmclennan@flatironinstitute.org

class EmpireSlurm:
    config = {
        "apiVersion": "v0.0.39",
        "apiServer": "alpha-mgr",
        "protocol": "http",
        "port": 6820,
    }

    def __init__(self):
        self.endPoints = {
            "diag": "slurm/" + self.config["apiVersion"] + "/diag",
            "accounts": "slurmdb/" + self.config["apiVersion"] + "/accounts",
            "account": "slurmdb/" + self.config["apiVersion"] + "/account/_NAME",
            "partitions": "slurm/" + self.config["apiVersion"] + "/partitions",
            "partition": "slurm/" + self.config["apiVersion"] + "/partition/_NAME",
        },

