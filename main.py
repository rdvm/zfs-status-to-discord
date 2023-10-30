from datetime import datetime, date, timedelta

# example output for testing
zStatus = """  pool: pool_1
 state: ONLINE
status: Some supported features are not enabled on the pool. The pool can
        still be used, but some features are unavailable.
action: Enable all features using 'zpool upgrade'. Once this is done,
        the pool may no longer be accessible by software that does not support
        the features. See zpool-features(5) for details.
  scan: scrub repaired 0B in 1 days 01:39:59 with 0 errors on Tue Oct 24 02:40:01 2023
config:

        NAME                                      STATE     READ WRITE CKSUM
        pool_1                                    ONLINE       0     0     0
          raidz1-0                                ONLINE       0     0     0
            7a194cdc-d479-11ec-8448-d05099c2ffc9  ONLINE       0     0     0
            5cc47781-d54a-11ec-8448-d05099c2ffc9  ONLINE       0     0     0
            c2d32d6d-d62a-11ec-a5d4-d05099c2ffc9  ONLINE       0     0     0
          raidz1-1                                ONLINE       0     0     0
            a8a6a8f4-1c6c-4d6e-ad65-7054477db014  ONLINE       0     0     0
            cf1c80ba-655f-4f67-8db7-a8dae4999a5f  ONLINE       0     0     0
            d3203934-b71a-4235-abdf-60c0a0ef117b  ONLINE       0     0     0

errors: No known data errors """


# returns a substring from zpool status by finding
# the index of the `start` and `end` parameters
def get_section(start, end, output=zStatus):
    words = output.split()
    indStart = words.index(start)
    indEnd = words.index(end)
    section = ""
    for i in range(indStart, indEnd):
        section += words[i] + " "
    return section.rstrip()


def get_state(start, end):
    section = get_section(start, end)
    if "ONLINE" in section:
        zfsHealthy = True


def get_status(start, end):
    section = get_section(start, end)


def get_scrub(start, end):
    section = get_section(start, end)
    words = section.split()
    mnum = datetime.strptime(words[-4], '%b').month
    scrubDate = datetime(int(words[-1]), mnum, int(words[-3])).date()
    scrubInterval = timedelta(days=7)

    if date.today() - scrubDate > scrubInterval:
        return f"The last scrub was on {scrubDate}, which is within defined tolerance."
    else:
        return f"The last scrub was on {scrubDate}, which is outside defined tolerance."


print(get_scrub("scan:", "config:"))
