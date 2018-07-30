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
    url = ('https://'+rubrik_clusters[cluster]['ip']+'/api/internal/cluster/me/io_stats?range=-10min')
    # create headers
    headers = {}
    auth = '{0}:{1}'.format(rubrik_clusters[cluster]['user'], rubrik_clusters[cluster]['pass'])
    auth = base64.encodestring(auth).replace('\n', '')
    headers['Authorization'] = 'Basic {0}'.format(auth)
    # get timestamp for 5 mins ago - format: 2018-01-16T00:00:00Z
    time = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
    time = str(time.isoformat())[:-7] + 'Z'
    parameters = {}
    parameters['limit'] = 9999
    parameters['after_date'] = time
    response = requests.get(url, params=parameters, headers=headers, verify=False)
    response = response.json()
    output={}
    output['clusterName'] = cluster_name
    output['time'] = response['iops']['readsPerSecond'][-1]['time']
    output['readsPerSecond'] = response['iops']['readsPerSecond'][-1]['stat']
    output['writesPerSecond'] = response['iops']['writesPerSecond'][-1]['stat']
    output['readBytePerSecond'] = response['ioThroughput']['readBytePerSecond'][-1]['stat']
    output['writeBytePerSecond'] = response['ioThroughput']['writeBytePerSecond'][-1]['stat']
    out_json = json.dumps(output)
    print out_json