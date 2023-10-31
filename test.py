from datetime import datetime, date, timedelta
from urllib.request import Request, urlopen
import json
import config
import subprocess


# Example zpool list
zList = """ NAME     SIZE  ALLOC   FREE  CKPOINT  EXPANDSZ   FRAG    CAP  DEDUP    HEALTH  ALTROOT
pool_1  87.2T  67.8T  19.4T        -         -     4%    77%  1.00x    ONLINE  - """

# zPoolList = subprocess.run(['/sbin/zpool', 'list'], stdout=subprocess.PIPE, universal_newlines=True)
# zList = zPoolList.stdout

zList = zList.split()

print(zList)
