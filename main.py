
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
