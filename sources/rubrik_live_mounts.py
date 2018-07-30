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
    output={}
    output['clusterName'] = cluster_name
    # Get Hyper-V Mounts
    url = ('https://'+rubrik_clusters[cluster]['ip']+'/api/internal/hyperv/vm/snapshot/mount')
    parameters = {}
    response = requests.get(url, params=parameters, headers=headers, verify=False)
    response = response.json()
    output['hypervMounts'] = response['total']
    # Get vSphere Mounts
    url = ('https://'+rubrik_clusters[cluster]['ip']+'/api/v1/vmware/vm/snapshot/mount')
    parameters = {}
    response = requests.get(url, params=parameters, headers=headers, verify=False)
    response = response.json()
    output['vmwareMounts'] = response['total']
    # Get MSSQL Mounts
    url = ('https://'+rubrik_clusters[cluster]['ip']+'/api/v1/mssql/db/mount')
    parameters = {}
    response = requests.get(url, params=parameters, headers=headers, verify=False)
    response = response.json()
    output['mssqlMounts'] = response['total']
    # Get Managed Volume Mounts
    url = ('https://'+rubrik_clusters[cluster]['ip']+'/api/internal/managed_volume/snapshot/export')
    parameters = {}
    response = requests.get(url, params=parameters, headers=headers, verify=False)
    response = response.json()
    output['mvMounts'] = response['total']
    output['total'] = output['hypervMounts']+output['vmwareMounts']+output['mssqlMounts']+output['mvMounts']
    out_json = json.dumps(output)
    print out_json