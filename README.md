# Template and scripts for monitoring bareos via API
That solution uses API to gather metrics from bareos, all you need to configure on bareos-dir side is a profile and user for monitoring (check examples *bareos-dir.d/console/zabbix.conf* and *bareos-dir.d/profile/monitoring.conf*)
## Features
* Gather data via API
* LLD discovery for active jobs
## Metrics & triggers
* Last job's status & size, job estimate size
* Bareos-dir health (via director's time metric)
* SQL connectivity (via total jobs metric)
## Requirements
* python 3 (for me works only with Python 3.13.1)
* python-bareos module 
## Installation
1. Configure bareos's profile and user for monitoring (check examples)
2. Install **python-bareos** module (it can be found in official repository since v18 or in pip `(python3.13 -m pip install uvicorn bareos-restapi sslpsk)`) 
3. Create config at **zabbix_bareos.yml**, set host, user and password:
```
---
host: bareos-dir.example.org
user: zabbix
password: ChangeMe
```
4. Run **bareos.discovery.py** to be sure that all was configured correctly (you should get valid JSON)
5. Put scripts in zabbix-agent scripts dir & set correct permissions
6. Put **userparameter_bareos.conf** in **zabbix_agentd.d** dir and restart agent
7. Import template
8. Assign template on host


## Problems

If you see a trigger in zabbix
```
---
Can't fetch data from bareos
---
```
or an error in the Bareos logs
```
---
bareos-dir: ERROR in dird/authenticate_console.cc:417 Number of console connections exceeded Maximum :20, Current: 451
---
```
You need to increase the limit of simultaneous connections to the console (by default it is 20). For this you need in  
add this parameter to the /etc/bareos/bareos-dir.d/director/bareos-dir.conf file
```
Maximum Console Connections = 200
```
