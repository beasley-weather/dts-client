Usage:

    export DTS_SERVER='example.com:123/data' \
           DTS_INTERVAL=60 \
           WEEWX_DATABASE=/var/lib/weewx/weewx.sdb
    python -m dts_client

Note that you must add the /data to the end. Currently it is hardcoded to take in a pull
path to the endpoint on the server
