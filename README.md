# snmp-system-supervisor
Use SNMP to supervise the usage of CPU/RAM/ROM and the collective upstream/downstream traffic.

## Setup
The code is running with python3. `pysnmp` is needed for SNMP. Remember to enable SNMP support on your PC. Prerequisite packages are `pysnmp`, `numpy` and `matplotlib`.
```bash
pip3 install pysnmp
pip3 install numpy
pip3 install matplotlib
```

## Function
1. Get the name of oid.
2. Get the value via oid
2. Set the value via oid.

## Start with GUI
Run `main.py` directly to start with GUI. The information of CPU/RAM/ROM usage and collective upstream/downstream traffic is shown on the interface. You can set a threshold to enable a CPU watchdog, which threws warning text when CPU is overloaded.

## Acknowledgment
This project serves as the submission of the SJTU EE380 curriculum design.
