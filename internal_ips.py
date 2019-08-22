import socket

servers = {'Web Front End - Development':['3lv11reoptw01.nrel.gov'],'Web Front End - Staging':['2lv12reoptw01.nrel.gov'],'Web Front End - Production':['1lv12reoptw01.nrel.gov','1lv12reoptw02.nrel.gov']}
internal_ips = {}
for k,v in servers.items():
	for vv in v:
		internal_ips[socket.gethostbyname(vv)] = k

