# GET Command Generator
from pysnmp.entity.rfc3413.oneliner import cmdgen
import time
import socket
import re

networkTemplate = [
		{
			'id'		:(1,3,6,1,2,1, 2,2,1,1),
			'name'		: 'network',
			'outValues' : ('ifBytesOut', 'ifBytesIn', 'ifStatus'),
			'outPattern': 'collectd.{0[config][target]}.{0[data][ifName]}.{1}'
		},
		{ 
			'ifName'    : (1,3,6,1,2,1,31,1,1,1, 1), 
			#'ifDesc'    : (1,3,6,1,2,1,31,1,1,1,18),
			'ifStatus'  : (1,3,6,1,2,1, 2,2,1,8),
			'ifBytesIn' : (1,3,6,1,2,1,31,1,1,1, 6),
			'ifBytesOut': (1,3,6,1,2,1,31,1,1,1,10)
		}
	]
	
snmpConfig = [
		{
			'target' : '127.0.0.1',
			'community' : 'public',
			'templates' : [networkTemplate]
		}
	]
		
carbonAddress = '127.0.0.1'
graphiteSocket = socket.create_connection((carbonAddress,2003))

def snmp_walk(snmpTarget, snmpCommunity, plainOID):
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


def writeGraphite(config, template, snmpTable):
	for templateName, snmpData in snmpTable.iteritems(): # template based dict
		for snmpValue, snmpData in snmpData.iteritems(): # snmpwalk based dict
			formatDict = dict()
			formatDict['config'] = config
			formatDict['config']['template'] = template
			formatDict['data'] = snmpData
			if 'id' not in template[0]:
				formatDict['dataIdentifier'] = snmpValue
			for output in template[0]['outValues']:
				metricName =  re.sub('\s', '_', template[0]['outPattern'].format(formatDict, output))
				graphiteString = []
				graphiteString.append(metricName)
				graphiteString.append(str(snmpData[output]))
				graphiteString.append(int(time.time()))
				graphiteString.append('\n')
				graphiteOutput = ' '.join(str(value) for value in graphiteString)
				print graphiteOutput
				graphiteSocket.send(graphiteOutput)

			#for name, data in snmpData.iteritems():
				#print '\t%s = %s' % (name, data)


for config in snmpConfig:
	snmpTarget = config['target']
	snmpCommunity = config['community']
	for template in config['templates']:
		snmpTable = dict()
		templateName = template[0]['name']

		snmpTable[templateName] = dict()

		if 'id' in template[0]:
			snmpIdentifierOid = template[0]['id']
			configTable = snmp_walk(snmpTarget, snmpCommunity, snmpIdentifierOid)

			for configValues in configTable:
				snmpTable[templateName][configValues[0][1]] = dict()

		for snmpName, snmpOid in template[1].iteritems():
			dataTable = snmp_walk(snmpTarget, snmpCommunity, snmpOid)
			for row in dataTable:
				for name, val in row:
					if 'id' in template[0]:
						snmpTable[templateName][name[-1]][snmpName] = val
					else:
						if name[-1] not in snmpTable[templateName]:
							snmpTable[templateName][name[-1]] = dict()
						snmpTable[templateName][name[-1]][snmpName] = val
		writeGraphite(config, template, snmpTable)