#!/usr/bin/python

#GraphML-Topo-to-Mininet-Network-Generator
#
# This file parses Network Topologies in GraphML format from the Internet Topology Zoo.
# A python file for creating Mininet Topologies will be created as Output.
# Files have to be in the same directory.
#
# Arguments:
#   -f              [filename to of GraphML input file]
#   --file          [filename to of GraphML input file]
#   -o              [filename to of GraphML output file]
#   --output        [filename to of GraphML output file]
#   -b              [number as integer for bandwidth in mbit]
#   --bw            [number as integer for bandwidth in mbit]
#   --bandwidth     [number as integer for bandwidth in mbit]
#   -c              [controller ip as string]
#   --controller    [controller ip as string]
#
# Without any input, program will terminate.
# Without specified output, outputfile will have the same name as the input file.
#
#
# Created by Stephan Schuberth in 01/2013 to 04/2013
#
#
# TODO's:
#   -   fix double name error of some topologies
#   -   fix topoparsing (choose by name, not element <d..>)
#           =    topos with duplicate labels
#   -   clean up
#   -   make ip parameter to set adress for remote controller
#   -   use formatted strings instead of this ugly concatenation
#   -   use 'argparse' for script parameters, eases help creation
#
#################################################################################



import xml.etree.ElementTree as ET
import sys
import math
import re
from sys import argv

input_file_name = ''
output_file_name = ''
bandwidth_argument = ''
controller_ip = ''

# first check commandline arguments
for i in range(len(argv)):
    if argv[i] == '-f':
        input_file_name = argv[i+1]
    if argv[i] == '--file':
        input_file_name = argv[i+1]
    if argv[i] == '-o':
        output_file_name = argv[i+1]
    if argv[i] == '--output':
        output_file_name = argv[i+1]
    if argv[i] == '-b':
        bandwidth_argument = argv[i+1]
    if argv[i] == '--bw':
        bandwidth_argument = argv[i+1]
    if argv[i] == '--bandwidth':
        bandwidth_argument = argv[i+1]
    if argv[i] == '-c':
        controller_ip = argv[i+1]
    if argv[i] == '--controller':
        controller_ip = argv[i+1]

# terminate when inputfile is missing
if input_file_name == '':
    sys.exit('\n\tNo input file was specified as argument....!')

# define string fragments for output later on
outputstring_1 = '''#!/usr/bin/python

"""
Custom topology for Mininet, generated by GraphML-Topo-to-Mininet-Network-Generator.
"""
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.node import Node
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

class GeneratedTopo( Topo ):
    "Internet Topology Zoo Specimen."

    def __init__( self, **opts ):
        "Create a topology."

        # Initialize Topology
        Topo.__init__( self, **opts )
'''

outputstring_2a='''
        # add nodes, switches first...
'''
outputstring_2b='''
        # ... and now hosts
'''

outputstring_3a='''
        # add edges between switch and corresponding host
'''

outputstring_3b='''
        # add edges between switches
'''

outputstring_4='''

topos = { 'generated': ( lambda: GeneratedTopo() ) }

# HERE THE CODE DEFINITION OF THE TOPOLOGY ENDS

# the following code produces an executable script working with a remote controller
# and providing ssh access to the the mininet hosts from within the ubuntu vm


def setupNetwork():
    "Create network and run simple performance test"
    topo = GeneratedTopo()
    # check if remote controller's ip was set
    # else set it to vbox standard: 10.0.2.2
    if controller_ip == '':
        controller_ip = '10.0.2.2';
    net = Mininet(topo=topo, controller=lambda a: RemoteController( a, ip=controller_ip, port=6633 ), host=CPULimitedHost, link=TCLink)
    return net


def connectToRootNS( network, switch, ip, prefixLen, routes ):
    """Connect hosts to root namespace via switch. Starts network.
      network: Mininet() network object
      switch: switch to connect to root namespace
      ip: IP address for root namespace node
      prefixLen: IP address prefix length (e.g. 8, 16, 24)
      routes: host networks to route to"""
    # Create a node in root namespace and link to switch 0
    root = Node( 'root', inNamespace=False )
    intf = TCLink( root, switch ).intf1
    root.setIP( ip, prefixLen, intf )
    # Start network that now includes link to root namespace
    network.start()
    # Add routes from root ns to hosts
    for route in routes:
        root.cmd( 'route add -net ' + route + ' dev ' + str( intf ) )


def sshd( network, cmd='/usr/sbin/sshd', opts='-D' ):
    "Start a network, connect it to root ns, and run sshd on all hosts."
    switch = network.switches[ 0 ]  # switch to use
    ip = '10.123.123.1'  # our IP address on host network
    routes = [ '10.0.0.0/8' ]  # host networks to route to
    connectToRootNS( network, switch, ip, 8, routes )
    for host in network.hosts:
        host.cmd( cmd + ' ' + opts + '&' )
    print
    print "*** Hosts are running sshd at the following addresses:"
    print

    for host in network.hosts:
        print host.name, host.IP()

    print "(If the topo breaks down HERE, check the xxx.graphml file for duplicate labels!)"
    print
    print "*** Type 'exit' or control-D to shut down network"
    CLI( network )
    for host in network.hosts:
        host.cmd( 'kill %' + cmd )
    network.stop()

if __name__ == '__main__':
    setLogLevel('info')
    #setLogLevel('debug')
    sshd( setupNetwork() )
'''

# WHERE TO PUT RESULTS
outputstring_to_be_exported = ''
outputstring_to_be_exported += outputstring_1

# READ FILE AND DO THE ACTUAL PARSING
tree = ET.parse(input_file_name)
namespace = "{http://graphml.graphdrawing.org/xmlns}"
ns = namespace # just doing shortcutting, namespaces are needed often.

root = tree.getroot()
graph = root.find(ns + 'graph')

#GET ALL ENTRIES
nodes = graph.findall(ns + 'node')
edges = graph.findall(ns + 'edge')

# NOW GENERATE THE ID'S
node_root_attrib = ''
node_name = ''
longitude = ''
latitude = ''
id_node_dict = {} # to hold all 'id: name' pairs
id_longitude_dict = {}
id_latitude_dict = {}


#GET ID DATA
#GET LONGITUDE DATK
#GET LATITUDE DATA
# FIXME here you have to set the correct 'dxy' settings.
# THESE MAY DIFFER IN THE DIFFERENT TOPOLOGY ZOO FILES!!!

for n in nodes:
    node_root_attrib = n.attrib['id']
    data = n.findall(ns + 'data')

    for d in data:
        #node name
    ## ABILENE network
        if d.attrib['key'] == 'd33':
            #next line strips all whitespace from names
            node_name = re.sub(r'\s+', '', d.text)
        #longitude data
        if d.attrib['key'] == 'd32':
            longitude = d.text
        #latitude data
        if d.attrib['key'] == 'd29':
            latitude = d.text
    ##DFN network
        #if d.attrib['key'] == 'd34':
            ##next line strips all whitespace from names
            #node_name = re.sub(r'\s+', '', d.text)
        #if d.attrib['key'] == 'd33':
            #longitude = d.text
        ##DFN network
        #if d.attrib['key'] == 'd30':
            #latitude = d.text
        #save data couple
        id_node_dict[node_root_attrib] = node_name
        id_longitude_dict[node_root_attrib] = longitude
        id_latitude_dict[node_root_attrib] = latitude


# FIRST CREATE THE SWITCHES AND HOSTS

tempstring1 = ''
tempstring2 = ''

for i in range(0, len(id_node_dict)):
    #create switch
    temp1 =  '        '
    temp1 += id_node_dict[str(i)]
    temp1 += " = self.addSwitch( 's"
    temp1 += str(i)
    temp1 += "' )\n"
    #create corresponding host
    temp2 =  '        '
    temp2 += id_node_dict[str(i)]
    temp2 += "_host = self.addHost( 'h"
    temp2 += str(i)
    temp2 += "' )\n"
    tempstring1 += temp1
    tempstring2 += temp2

outputstring_to_be_exported += outputstring_2a
outputstring_to_be_exported += tempstring1
outputstring_to_be_exported += outputstring_2b
outputstring_to_be_exported += tempstring2
outputstring_to_be_exported += outputstring_3a


# SECOND CALCULATE DISTANCES BETWEEN SWITCHES,
#   set global bandwidth and create the edges between switches,
#   and link each single host to its corresponding switch

tempstring3 = ''
tempstring4 = ''
distance = 0.0
latency = 0.0

for e in edges:
    # GET IDS FOR EASIER HANDLING
    src_id = e.attrib['source']
    dst_id = e.attrib['target']
    # CALCULATE

        #formula: (for distance)
        #dist(SP,EP) = arccos{ sin(La[EP]) * sin(La[SP]) + cos(La[EP]) * cos(La[SP]) * cos(Lo[EP] - Lo[SP])} * r
        #r = 6378.137 km
        #formula: (speed of light)
        # v = 2.3 * 10**8 m/s
        #formula: (latency being calculated from distance and light speed)
        #t = distance / speed of light
        #t (in ms) = ( distance in km * 1000 (for meters) ) / ( speed of light / 1000 (for ms))

    firstproduct = math.sin(float(id_latitude_dict[dst_id])) * math.sin(float(id_latitude_dict[src_id]))
    secondproductfirstpart = math.cos(float(id_latitude_dict[dst_id])) * math.cos(float(id_latitude_dict[src_id]))
    secondproductsecondpart = math.cos((float(id_longitude_dict[dst_id])) - (float(id_longitude_dict[src_id])))
    distance = math.radians(math.acos(firstproduct + (secondproductfirstpart * secondproductsecondpart))) * 6378.137

    #t (in ms) = ( distance in km * 1000 (for meters) ) / ( speed of light / 1000 (for ms))
    latency = ( distance * 1000 ) / ( 230000 )

    # BANDWIDTH LIMITING
    #set bw to 10mbit if nothing was specified otherwise on startup
    if bandwidth_argument == '':
        bandwidth_argument = '10';

    # link each switch and its host...
    temp3 =  '        self.addLink( '
    temp3 += id_node_dict[src_id]
    temp3 += ' , '
    temp3 += id_node_dict[src_id]
    temp3 += "_host )"
    temp3 += '\n'
    # ... and link all corresponding switches with each other
    temp4 =  '        self.addLink( '
    temp4 += id_node_dict[src_id]
    temp4 += ' , '
    temp4 += id_node_dict[dst_id]
    temp4 += ", bw="
    temp4 += bandwidth_argument
    temp4 += ", delay='"
    temp4 += str(latency)
    temp4 += "ms')"
    temp4 += '\n'
    # next line so i dont have to look up other possible settings
    #temp += "ms', loss=0, max_queue_size=1000, use_htb=True)"
    tempstring3 += temp3
    tempstring4 += temp4

outputstring_to_be_exported += tempstring3
outputstring_to_be_exported += outputstring_3b
outputstring_to_be_exported += tempstring4
outputstring_to_be_exported += outputstring_4


# GENERATION FINISHED, WRITE STRING TO FILE
outputfile = ''
if output_file_name == '':
    output_file_name = input_file_name + '-generated-Mininet-Topo.py'

outputfile = open(output_file_name, 'w')
outputfile.write(outputstring_to_be_exported)
outputfile.close()

print "Topology generation SUCCESSFUL!"
