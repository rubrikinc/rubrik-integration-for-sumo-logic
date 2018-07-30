#!/usr/bin/python
import datetime
import requests
import json
import base64
import os

no_cert_warnings = True
rubrik_clusters = {
    'cluster-1':{
        'ip':'10.100.1.10',
        'user':'admin',
        'pass':'pass123!'
    },
    'cluster-2':{
        'ip':'10.100.2.10',
        'user':'admin',
        'pass':'pass123!'
    }
}

if no_cert_warnings:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

for cluster in rubrik_clusters:
    # get our cluster name first
    url = ('https://'+rubrik_clusters[cluster]['ip']+'/api/v1/cluster/me')
    # create headers
    headers = {}
    auth = '{0}:{1}'.format(rubrik_clusters[cluster]['user'], rubrik_clusters[cluster]['pass'])
    auth = base64.encodestring(auth).replace('\n', '')
    headers['Authorization'] = 'Basic {0}'.format(auth)
    parameters = {}
    response = requests.get(url, params=parameters, headers=headers, verify=False)
    response = response.json()
    cluster_name = response['name']
    # done with getting cluster name
    url = ('https://'+rubrik_clusters[cluster]['ip']+'/api/internal/event')
    # create headers
    headers = {}
    auth = '{0}:{1}'.format(rubrik_clusters[cluster]['user'], rubrik_clusters[cluster]['pass'])
    auth = base64.encodestring(auth).replace('\n', '')
    headers['Authorization'] = 'Basic {0}'.format(auth)
    # get timestamp for 5 mins ago - format: 2018-01-16T00:00:00Z
    time = datetime.datetime.utcnow() - datetime.timedelta(minutes=20)
    time = str(time.isoformat())[:-7] + 'Z'
    parameters = {}
    parameters['limit'] = 9999
    parameters['after_date'] = time
    response = requests.get(url, params=parameters, headers=headers, verify=False)
    response = response.json()
    for event in response['data']:
        if (event['eventStatus'] in ['Failure','Warning','Success','Canceled']):
            this_record = {}
            event_info = json.loads(event['eventInfo'])
            this_record['eventType'] = event['eventType']
            this_record['objectId'] = event['objectId']
            if ('objectName' in event.keys()):
                this_record['objectName'] = event['objectName']
            this_record['objectType'] = event['objectType']
            this_record['eventStatus'] = event['eventStatus']
            this_record['id'] = event['id']
            this_record['time'] = event['time']
            this_record['message'] = event_info['message']
            this_record['clusterName'] = cluster_name
            if ('${locationName}' in event_info['params'].keys()):
                this_record['locationName'] = event_info['params']['${locationName}']
            if ('${username}' in event_info['params'].keys()):
                this_record['username'] = event_info['params']['${username}']
            if ('${orgName}' in event_info['params'].keys()):
                this_record['orgName'] = event_info['params']['${orgName}']
            if ('${orgId}' in event_info['params'].keys()):
                this_record['orgId'] = event_info['params']['${orgId}']
            out_json = json.dumps(this_record)
            print out_json