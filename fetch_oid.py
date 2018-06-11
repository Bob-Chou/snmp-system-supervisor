from utils import *
import sys

print('\nInput OID: ')
line = sys.stdin.readline().strip()
while line:
	try:
		name, value = get_oid_value(line)
		print('OID name: {}, OID value: {}'.format(name, value))
	except:
		print('Invalid input, process terminated.')
		break
	print('\nInput OID: ')
	line = sys.stdin.readline().strip()
