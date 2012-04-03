#!/usr/bin/python
"""A simple helper script that retrieves a Keystone authentication
token given a keystone URL, username, password and tenant name, and
returns an OCF-compliant error code on exit."""

# OCF error codes.
# OCF_ERR_GENERIC conveniently matches the exit code of
# sys.exit(string)
OCF_SUCCESS=0
OCF_ERR_GENERIC=1
OCF_ERR_ARGS=2
OCF_ERR_UNIMPLEMENTED=3
OCF_ERR_PERM=4
OCF_ERR_INSTALLED=5
OCF_ERR_CONFIGURED=6
OCF_NOT_RUNNING=7

import sys
try:
    import json
    import urllib2
except ImportError:
    sys.exit(OCF_ERR_INSTALLED)

def get(url, username, password, tenant_name):
    auth = { "auth" : 
             { "passwordCredentials" : 
               { "username" : username ,
                 "password" : password,
                 "tenant_name" : tenant_name }
               }
             }
    headers = {'Content-Type': 'application/json'}
                 
    data = json.dumps(auth)
    req = urllib2.Request(url, data, headers)
    res = ""
    try:
        f = urllib2.urlopen(req)
        res = f.read()
        f.close()
    except:
        sys.exit("JSON request to %s failed" % url)

    try:
        token = json.loads(res)
        print token['access']['token']['id']
    except KeyError:
        sys.exit("Unable to retrieve access token for user %s (tenant %s) from %s" 
                 % (username, tenant_name, url))

def check(url, token):
    headers = {'Content-Type': 'application/json',
               'X-Auth-Token': token}

    req = urllib2.Request(url, "", headers)
    try:
        f = urllib2.urlopen(req)
        token = f.read()
        f.close()
    except:
        sys.exit("Token validation at %s failed" % url)


if __name__ == '__main__':
    methods = [ "get", "check" ]

    try:
        method = sys.argv[1]
    except IndexError:
        sys.exit("Insufficient number of arguments")
        
    if method not in methods:
        sys.exit("Unsupported method (must be one of %s)" % methods)

    try:
        url = sys.argv[2]
        if method == "get":
            username = sys.argv[3]
            password = sys.argv[4]
            tenant_name = sys.argv[5]
            get(url, username, password, tenant_name)
        elif method == "check":
            token = sys.argv[3]
            check(url, token)
    except IndexError:
        sys.exit("Insufficient number of arguments")
