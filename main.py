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
    capVal = [capacity]

    if capacity >= 80:
        capVal.append(f"**WARNING** Pool used capacity is **{capacity}%**. It is recommended to stay under 80%")
        capVal.append(False)
    else:
        capVal.append(f"Pool used capacity is **{capacity}%**. It is recommended to stay under 80%")
        capVal.append(True)

    return capVal


# returns a substring from zpool status by finding
# the index of the `start` and `end` parameters
def get_section(start, end):
    z_status = subprocess.run(['/sbin/zpool', 'status'], stdout=subprocess.PIPE, universal_newlines=True).stdout
    words = z_status.split()
    indStart = words.index(start)
    indEnd = words.index(end)
    sectVal = [words[indStart]]
    section = ""

    for i in range(indStart + 1, indEnd):
        section += words[i] + " "
    sectVal.append(section)

    return sectVal


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
    scrubDate = datetime(int(words[-1]), mnum, int(words[-3])).date()
    scrubInterval = timedelta(days=1)

    if (date.today() - scrubDate) < scrubInterval:
        section.append(True)
        section.append(f"The last scrub was on {scrubDate}, which is within defined tolerance.")
        return section
    else:
        section.append(False)
        section.append(f"The last scrub was on {scrubDate}, which is **outside defined tolerance.**")
        return section


# Set discord variables depending on health status
def zfs_report():
    stateMsg = get_state()
    statusMsg = get_status()
    scanMsg = get_scrub()
    capMsg = get_capacity()

    if stateMsg[2] is True and scanMsg[2] is True and capMsg[2] is True:
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
                  "name": stateMsg[0].capitalize(),
                  "value": stateMsg[1]
                },
                {
                  "name": "Pool Utilization",
                  "value": capMsg[1]
                },
                {
                  "name": statusMsg[0].capitalize(),
                  "value": statusMsg[1]
                },
                {
                  "name": scanMsg[0].capitalize(),
                  "value": scanMsg[3]
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
