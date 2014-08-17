docker-dnsimple-updater
=======================

Simple Docker container for updating IP address with DNSimple. Uses a quickly knocked
together Python script. Attempt will be made to update both IPv6 (AAAA) and IPv4 (A) addresses
for a host.

    OS Base : Ubuntu 14.04

Environment Variables
---------------------
  DNSIMPLE_DOMAIN
    The domain you would like to manage
  DNSIMPLE_HOST
    The host you would like to update
  DNSIMPLE_DOMAIN_TOKEN
    Domain API Token, you can find this on the https://dnsimple.com/domains/${DNSIMPLE_DOMAIN}
  UPDATE_INTERVAL
    Time you would like to wait between updates. Use an integer followed by either 's', 'm', 'h'
    for either sec, minute, hour. Example '30s', '45m' '2h'

Configuration File
------------------
You can provide a JSON configuration mounted on /dnsimple.json. An exmaple can be found below

```
{
  "domain": "example.com",
  "host": "myhost",
  "api_token": "XXXXXXXXXX123456789",
  "update": "30m"
}
```

Note: Environment variables override configuration file options.

TODO
----
  [ ] Add option to specify TTL
  [ ] Better logging, show messages without needing `-t`

