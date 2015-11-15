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

```json
{
  "domain": "example.com",
  "host": "myhost",
  "api_token": "XXXXXXXXXX123456789",
  "update": "30m"
}
```

Note: Environment variables override configuration file options.

#### IP Lookup URLS
The following URLS are used for lookups:

###### IPv4
- http://ipinfo.io/ip
- http://ipv4.icanhazip.com
- http://ipecho.net/plain
- http://ident.me/

###### IPv6
- http://v6.ident.me/
- http://ip6.telize.com/
- http://ipv6.icanhazip.com

Lookups are performed in order and the script will use the first match. You can override these URLS by adding `lookup_urls` hash to the config file (environment variable not supported). Example:

```json
"lookup_urls": {
                  "ipv4": [ "http://some.ipv4.url", "http://another.ipv4.url" ],
                  "ipv6": [ "http://some.ipv6.url", "http://another.ipv6.url" ]
               }
```

TODO
----
- [ ] Add option to specify TTL
- [ ] Better logging, show messages without needing `-t`
- [x] Support user specified Lookup URLS

