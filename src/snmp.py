# GET Command Generator
from pysnmp.entity.rfc3413.oneliner import cmdgen
import time
import socket

snmpTarget = '127.0.0.1'
snmpCommunity = 'public'
carbonAddress = '127.0.0.1'

def snmp_walk(plainOID):
	errorIndication, errorStatus, \
    	             errorIndex, varBindTable = cmdgen.CommandGenerator().nextCmd(
	    # SNMP v1
	#    cmdgen.CommunityData('test-agent', 'public', 0),
	    # SNMP v2
	    cmdgen.CommunityData('test-agent', snmpCommunity),
	    # SNMP v3
	#    cmdgen.UsmUserData('test-user', 'authkey1', 'privkey1'),
	    cmdgen.UdpTransportTarget((snmpTarget, 161)),
	    # Plain OID
	    plainOID
	    # ((mib-name, mib-symbol), instance-id)
	    #(('SNMPv2-MIB', 'sysObjectID'), 0)
	    )

	if errorIndication:
	    print errorIndication	
	else:
	    if errorStatus:
	        print '%s at %s\n' % (
	            errorStatus.prettyPrint(),
	            errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
	            )
	    else:
	    	return varBindTable
	        for varBindTableRow in varBindTable:
				for name, val in varBindTableRow:
					print '%s = %s' % (name.prettyPrint(), val.prettyPrint())

snmpTable = dict()

ifIds = (1,3,6,1,2,1,2,2,1,1)
dataTable = snmp_walk(ifIds)

for varBindTableRow in dataTable:
	snmpTable[varBindTableRow[0][1]] = dict()
	#for name, val in varBindTableRow:
	#	print '%s = %s' % (name.prettyPrint(), val.prettyPrint())
		
ifName = (1,3,6,1,2,1,31,1,1,1,1)
dataTable = snmp_walk(ifName)

for varBindTableRow in dataTable:
#	snmpTable[]
	for name, val in varBindTableRow:
		snmpTable[name[-1]]['ifName'] = val
		
ifDesc = (1,3,6,1,2,1,31,1,1,1,18)
dataTable =  snmp_walk(ifDesc)

for varBindTableRow in dataTable:
#	snmpTable[]
	for name, val in varBindTableRow:
		snmpTable[name[-1]]['ifDesc'] = val
		
ifStatus = (1,3,6,1,2,1,2,2,1,8)
dataTable =  snmp_walk(ifStatus)

for varBindTableRow in dataTable:
#	snmpTable[]
	for name, val in varBindTableRow:
		snmpTable[name[-1]]['ifStatus'] = val

#ifSpeed = (1,3,6,1,2,1,2,2,1,5)
#dataTable =  snmp_walk(ifSpeed)
#
#for varBindTableRow in dataTable:
#	snmpTable[]
#	for name, val in varBindTableRow:
#		print '%s = %s' % (name.prettyPrint(), val.prettyPrint())
#		print name[-1]
#		snmpTable[name[-1]]['ifSpeed'] = val
#
ifBytesIn = (1,3,6,1,2,1,31,1,1,1,6)
dataTable =  snmp_walk(ifBytesIn)

for varBindTableRow in dataTable:
#	snmpTable[]
	for name, val in varBindTableRow:
		snmpTable[name[-1]]['ifBytesIn'] = val

ifBytesOut = (1,3,6,1,2,1,31,1,1,1,10)
dataTable =  snmp_walk(ifBytesOut)

for varBindTableRow in dataTable:
#	snmpTable[]
	for name, val in varBindTableRow:
		snmpTable[name[-1]]['ifBytesOut'] = val


#print snmpTable
graphiteSocket = socket.create_connection((carbonAddress,2003))


#snmp_walk((1,3,6,1,2,1,31,1,1,1,1))
outputValues = ('ifBytesOut', 'ifBytesIn', 'ifStatus')
for snmpValue, snmpData in snmpTable.iteritems():
	print snmpValue
	
	for output in outputValues:
		graphiteData = []
		graphiteData.append('collectd')
		graphiteData.append(snmpTarget)
		graphiteData.append(snmpData['ifName'])
		graphiteData.append(output)
		graphiteString = []
		graphiteString.append('.'.join(str(name) for name in graphiteData))
		graphiteString.append(snmpData[output])
		graphiteString.append(int(time.time()))
		graphiteString.append('\n')
		graphiteOutput = ' '.join(str(value) for value in graphiteString)
		print graphiteOutput
		graphiteSocket.send(graphiteOutput)

	for name, data in snmpData.iteritems():
		print '\t%s = %s' % (name, data)

