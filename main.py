#!/usr/bin/env python3

from datetime import datetime, date, timedelta
from urllib.request import Request, urlopen
import json
import subprocess
import config


# Get capacity info
def get_capacity():
    z_list = subprocess.run(['/sbin/zpool', 'list'], stdout=subprocess.PIPE, universal_newlines=True).stdout
    words = z_list.split()
    capacity = int(words[18].rstrip('%'))
    cap_val = [capacity]

    if capacity >= 80:
        cap_val.append(f"**WARNING** Pool used capacity is **{capacity}%**. It is recommended to stay under 80%")
        cap_val.append(False)
    else:
        cap_val.append(f"Pool used capacity is **{capacity}%**. It is recommended to stay under 80%")
        cap_val.append(True)

    return cap_val


# returns a substring from zpool status by finding
# the index of the `start` and `end` parameters
def get_section(start, end):
    z_status = subprocess.run(['/sbin/zpool', 'status'], stdout=subprocess.PIPE, universal_newlines=True).stdout
    words = z_status.split()
    ind_start = words.index(start)
    ind_end = words.index(end)
    sect_val = [words[ind_start]]
    section = ""

    for i in range(ind_start + 1, ind_end):
        section += words[i] + " "
    sect_val.append(section)

    return sect_val


# get the 'state:' section and set a boolean to indicate health
def get_state():
    section = get_section("state:", "status:")

    if section[1].strip() == "ONLINE":
        section.append(True)
        return section
    else:
        section.append(False)
        return section


# get the 'status:' section
def get_status():
    return get_section("status:", "action:")


# get the 'scan:' section for scrub info
def get_scrub():
    section = get_section("scan:", "config:")
    words = section[1].split()
    mnum = datetime.strptime(words[-4], '%b').month
    scrub_date = datetime(int(words[-1]), mnum, int(words[-3])).date()
    scrub_interval = timedelta(days=7)

    if (date.today() - scrub_date) < scrub_interval:
        section.append(True)
        section.append(f"The last scrub was on {scrub_date}, which is within defined tolerance.")
        return section
    else:
        section.append(False)
        section.append(f"The last scrub was on {scrub_date}, which is **outside defined tolerance.**")
        return section


# Set discord variables depending on health status
def zfs_report():
    state_msg = get_state()
    status_msg = get_status()
    scan_msg = get_scrub()
    cap_msg = get_capacity()

    if state_msg[2] is True and scan_msg[2] is True and cap_msg[2] is True:
        discord_title = "✅ ZFS Health Report ✅"
        discord_webhook = config.discord_info_webhook
        discord_color = 4378646
    else:
        discord_title = "🚨 ZFS Health Report -- ATTENTION!! 🚨"
        discord_webhook = config.discord_alert_webhook
        discord_color = 14177041

    message = {
        "username": "ZFSBot",
        "embeds": [
            {
              "color": discord_color, "title": discord_title,
              "fields": [
                {
                  "name": state_msg[0].capitalize(),
                  "value": state_msg[1]
                },
                {
                  "name": "Pool Utilization",
                  "value": cap_msg[1]
                },
                {
                  "name": status_msg[0].capitalize(),
                  "value": status_msg[1]
                },
                {
                  "name": scan_msg[0].capitalize(),
                  "value": scan_msg[3]
                }
              ]
            }
        ]
    }

    req = Request(discord_webhook, json.dumps(message).encode('utf-8'))

    # discord appears to block the default urllib user-agent
    # specifying headers for the request
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11')

    response = urlopen(req)
    response.read()


def main():
    zfs_report()


main()
