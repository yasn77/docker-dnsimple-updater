#!/usr/bin/env python

import requests
import json
import os
import time

import pprint

config_file = '/dnsimple.json'
env_vars_map = {
                'DNSIMPLE_DOMAIN': 'domain',
                'DNSIMPLE_HOST': 'host',
                'DNSIMPLE_DOMAIN_TOKEN': 'api_token',
                'UPDATE_INTERVAL': 'update'
               }

def get_config():
    config = {}
    try:
        with open(config_file) as d:
            config = json.load(d)
    except:
        pass

    for k,v in env_vars_map.iteritems():
        if k in os.environ.keys():
            config[v] = os.environ[k]
    return config

def __log(msg):
    print('{0} {1}').format(time.strftime("%Y-%m-%dT%H:%M:%S"), msg)

def to_sec(u, v):
    if u == 's':
        return int(v)
    elif u == 'm':
        return int(v) * 60
    elif u == 'h':
        return int(v) * 3600
    else:
        return int(v)

def get_ext_ip():
    ipv6 = None
    ipv4 = None
    try:
        ipv4 = requests.get('http://jsonip.com').json()['ip']
    except:
        __log('WARN: Failed to get ipv4 from http://jsonip.com')

    if ipv4 == None:
        try:
            ipv4 = requests.get('http://ipv4.icanhazip.com').text.strip()
        except:
            __log('WARN: Failed to get ipv4 from http://ipv4.icanhazip.com')

    try:
        ipv6 = requests.get('http://ipv6.icanhazip.com').text.strip()
    except:
        __log('WARN: Failed to get ipv6 from http://ipv6.icanhazip.com')

    if ipv6 == None:
        try:
            ipv6 = requests.get('http://ip6.telize.com/').text.strip()
        except:
            __log('WARN: Failed to get ipv6 from http://ip6.telize.com/')
    return (ipv4, ipv6)

def create_record(name, record_type, content):
    headers = {
                'X-DNSimple-Domain-Token': config['api_token'],
                'Accept': 'application/json',
                'Content-Type': 'application/json'
             }
    url = 'https://api.dnsimple.com/v1/domains/{0}/records'.format(config['domain'])
    payload = { 'record': { 'name': name, 'content': content, 'record_type': record_type} }
    try:
        __log('Creating "{0}" record for {1} using IP {2}'.format(record_type, name, content))
        resp = requests.post(url, headers=headers, data=json.dumps(payload))
    except e:
        __log('ERR: Problem creating "{0}" record for {1} using IP {2}'.format(record_type, name, content))

def update_record(record, content):
    headers = {
                'X-DNSimple-Domain-Token': config['api_token'],
                'Accept': 'application/json',
                'Content-Type': 'application/json'
             }
    url = 'https://api.dnsimple.com/v1/domains/{0}/records/{1}'.format(config['domain'],record['id'])
    if record['content'] == content:
        __log('"{0}" record content is already set to {1} for {2}... Skipping update'.format(record['record_type'], content, record['name']))
        return
    else:
        payload = { 'record': { 'name': record['name'], 'content': content, } }
        try:
            __log('Updating record {0} for {1} using IP {2}'.format(record['id'], record['name'], content))
            requests.request('PUT', url, headers=headers, data=json.dumps(payload))
        except:
            __log('Problem updating record {0} for {1} using IP {2}'.format(record['id'], record['name'], content))

def main():
    headers = {
                'X-DNSimple-Domain-Token': config['api_token'],
                'Accept': 'application/json'
             }
    unit = config['update'][-1].lower()
    if unit.isalpha():
        interval = config['update'][0:-1]
    else:
        interval = config['update']

    __log('DNSimple updater starting...')
    __log('CONFIG:')
    for k,v in config.iteritems():
        __log('{0}{1}: {2}'.format('\t',k,v))

    try:
        sec = to_sec(unit, interval)
    except ValueError:
        __log('ERR: Update interval is set to: {0}'.format(config['update']))
        __log('ERR: Problem trying to convert {0} to seconds...exiting'.format(interval))
        exit(1)


    while True:
        config['ipv4'], config['ipv6'] = get_ext_ip()
        ipv4_record = None
        ipv6_record = None
        if config['ipv4'] == None and config['ipv6'] == None:
            have_ip = False
        else:
            have_ip = True
        try:
            domain_records = requests.get('https://api.dnsimple.com/v1/domains/{0}/records'.format(config['domain']), headers=headers).json()
        except:
            domain_records = None
        if not domain_records == None and have_ip:
            __log('About to update:')
            __log('{0}FQDN: {1}.{2} IPV4: {3} IPV6: {4}'.format(
                '\t',
                config['host'],
                config['domain'],
                config['ipv4'],
                config['ipv6']
            ))
            for r in domain_records:
                if r['record']['name'] == config['host']:
                    cname_found = True if r['record']['record_type'] == 'CNAME' else False
                    ipv4_record = r['record'] if r['record']['record_type'] == 'A' else ipv4_record
                    ipv6_record = r['record'] if r['record']['record_type'] == 'AAAA' else ipv6_record
            if cname_found:
                __log('WARN: {0} has a CNAME record, please delete before trying to update... Skipping update'.format(config['host']))
                __log('Will sleep for {0} sec'.format(sec))
                time.sleep(sec)
                continue
            else:
                if not config['ipv4'] == None:
                    if ipv4_record == None:
                        pprint.pprint(ipv4_record)
                        create_record(config['host'], 'A', config['ipv4'])
                    else:
                        update_record(ipv4_record, config['ipv4'])
                if not config['ipv6'] == None:
                    if ipv6_record == None:
                        create_record(config['host'], 'AAAA', config['ipv6'])
                    else:
                        update_record(ipv6_record, config['ipv6'])
        else:
            __log('WARN: Did not get any domain records for {0} or could not find external address for IPv4 and IPv6... skipping update this time'.format(config['domain']))
        __log('Will sleep for {0} sec'.format(sec))
        time.sleep(sec)

if __name__ == '__main__':
    config = get_config()
    main()
