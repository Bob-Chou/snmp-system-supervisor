from utils import get_oid_value, set_oid_vale
import sys

print('\nInput OID: ')
line = sys.stdin.readline().strip()
print('\nInput New Value: ')
value = sys.stdin.readline().strip()

try:
	name, value = get_oid_value(line)
	print('old value before setting:')
	print('{} = {}'.format(name, value))
	name, value = set_oid_vale(line, value)
	print('Set finished, results:')
	print('{} = {}'.format(name, value))
except:
	print('Invalid input, process terminated.')