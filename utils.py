from pysnmp.entity.rfc3413.oneliner import cmdgen
import re

def get_oid_config(filename):
	config = {}
	with open(filename, 'r') as f:
		config = {line.strip().split(':')[0]:line.strip().split(':')[1] for line in f}
	return config


def set_oid_vale(oid, value):
	cmdGen = cmdgen.CommandGenerator()
	errorIndication, errorStatus, errorIndex, varBinds = cmdGen.setCmd(
		cmdgen.CommunityData('public'),
		cmdgen.UdpTransportTarget(('127.0.0.1', 161)),
		(oid, value)
	)

	# Check for errors and print out results
	if errorIndication:
		print(errorIndication)
		return None, None
	else:
		if errorStatus:
			print('%s at %s' % (
					errorStatus.prettyPrint(),
					errorIndex and varBinds[int(errorIndex)-1] or '?'
				)
			)
			return None, None
		else:
			for name, val in varBinds:
				return name.prettyPrint(), val.prettyPrint()

def get_oid_value(oid):
	cmdGen = cmdgen.CommandGenerator()
	errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
		cmdgen.CommunityData('public'),
		cmdgen.UdpTransportTarget(('127.0.0.1', 161)),
		oid
	)
	# Check for errors and print out results
	if errorIndication:
		print(errorIndication)
		return None, None
	else:
		if errorStatus:
			print('%s at %s' % (
				errorStatus.prettyPrint(),
				errorIndex and varBinds[int(errorIndex)-1] or '?'
				)
			)
			return None, None
		else:
			for name, val in varBinds:
				return name.prettyPrint(), val.prettyPrint()

def get_cpu_usage(oid_dicts):
	keys = oid_dicts.keys()
	cpu_oid = [k for k in keys if re.match('cpu-[0-9]* usage', k)]
	cpu_cnt = len(cpu_oid)
	average_usage = 0
	for oid in cpu_oid:
		_, value = get_oid_value(oid_dicts[oid])
		average_usage += int(value)/cpu_cnt
	return average_usage

def get_memory(oid_dicts):
	keys = oid_dicts.keys()
	mem_oid = ['physical-memory usage', 'physical-memory allocation', 'physical-memory storage']
	_, allocation = get_oid_value(oid_dicts['physical-memory allocation'])
	_, storage = get_oid_value(oid_dicts['physical-memory storage'])
	_, usage = get_oid_value(oid_dicts['physical-memory usage'])
	mem_total = int(allocation) * int(storage) / 1024 / 1024 / 1024
	mem_usage = int(allocation) * int(usage) / 1024 / 1024 / 1024
	return mem_total, mem_usage

def get_disk(oid_dicts):
	keys = oid_dicts.keys()
	names = sorted([k.split(' ')[0].split('-')[-1] for k in keys if re.match('disk-[C-Z] info', k)])
	disk_utils = {}
	for name in names:
		allocation = int(get_oid_value(oid_dicts['disk-{} allocation'.format(name)])[-1])
		storage = int(get_oid_value(oid_dicts['disk-{} storage'.format(name)])[-1])
		usage = int(get_oid_value(oid_dicts['disk-{} usage'.format(name)])[-1])
		total = allocation * storage / 1024 / 1024 / 1024
		usage = allocation * usage / 1024 / 1024 / 1024
		if total > 0:
			disk_utils[name] = [total, usage]
	return disk_utils

def get_network(oid_dicts):
	return int(get_oid_value(oid_dicts['network in'])[1])/1024/1024, int(get_oid_value(oid_dicts['network out'])[1])/1024/1024