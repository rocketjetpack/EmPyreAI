import getpass
from pythoncm.cluster import Cluster
from pythoncm.settings import Settings

CMSH_Cluster = None

if getpass.getuser() != "root":
     settings = Settings(
        host="alpha-mgr",
        port=8081,
        cert_file=f'/mnt/home/{getpass.getuser()}/.empireai/cmsh_api.pem',
        key_file=f'/mnt/home/{getpass.getuser()}/.empireai/cmsh_api.key',
        ca_file='/usr/lib64/python3.9/site-packages/pythoncm/etc/cacert.pem'
     )
     CMSH_Cluster = Cluster(settings)
     print("Initialized connection to CMSH_Cluster")
else:
     CMSH_Cluster = Cluster()
