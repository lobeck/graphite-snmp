# GET Command Generator
from pysnmp.entity.rfc3413.oneliner import cmdgen
import time
import socket

snmpTemplate = [
		{
			'id'		:(1,3,6,1,2,1, 2,2,1,1)
		},
		{ 
			'ifName'    : (1,3,6,1,2,1,31,1,1,1, 1), 
			'ifDesc'    : (1,3,6,1,2,1,31,1,1,1,18),
			'ifStatus'  : (1,3,6,1,2,1, 2,2,1,8),
			'ifBytesIn' : (1,3,6,1,2,1,31,1,1,1, 6),
			'ifBytesOut': (1,3,6,1,2,1,31,1,1,1,10)
		}
	]
	
#snmpConfig = {'127.0.0.1' : }
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
	        #for varBindTableRow in varBindTable:
			#	for name, val in varBindTableRow:
			#		print '%s = %s' % (name.prettyPrint(), val.prettyPrint())


print snmpTemplate
snmpTable = dict()
for config in snmpTemplate:
	if 'id' in config:
		configTable = snmp_walk(config['id'])
		for configValues in configTable:
			snmpTable[configValues[0][1]] = dict()
	else:
		for snmpName, snmpOid in config.iteritems():
			dataTable = snmp_walk(snmpOid)
			for row in dataTable:
				for name, val in row:
					snmpTable[name[-1]][snmpName] = val
	
#graphiteSocket = socket.create_connection((carbonAddress,2003))

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
		#graphiteSocket.send(graphiteOutput)

	for name, data in snmpData.iteritems():
		print '\t%s = %s' % (name, data)

