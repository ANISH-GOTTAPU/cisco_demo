import time

from ixnetwork_restpy import *


def test_restpy(request):

    tx_bgpd = {
        "Name":  "tx_bgpd",
        "MAC":   "00:10:94:00:01:91",
        "IPv4":  "166.1.1.2",
        "IPv4_routes": "10.1.1.1",
        "IPv6_routes": "10:1:1:1:1:1:1:1"
    }

    tx_isisd = {
        "Name":  "tx_isisd",
        "MAC":   "00:10:94:00:01:AB",
        "IPv4":  "170.1.1.2",
        "IPv6":  "170:1:1::2",
        "IPv4_routes": "30.1.1.1",
    }

    rx_bgpd = {
        "Name":  "rx_bgpd",
        "MAC":   "00:10:94:00:01:AC",
        "IPv4":  "166.1.1.1",
        "IPv4_routes": "20.1.1.1",
        "IPv6_routes": "20:1:1:1:1:1:1:1"
    }

    rx_isisd = {
        "Name":  "rx_isisd",
        "MAC":   "00:10:94:00:01:AD",
        "IPv4":  "170.1.1.1",
        "IPv6":  "170:1:1::1",
        "IPv4_routes": "40.1.1.1",
    }

    apiServerIp, port = request.config.getoption("--host").split(":")

    ixChassisIpList = request.config.getoption("--p1").split(";")[0]
    port1 = request.config.getoption("--p1").split(";")
    port2 = request.config.getoption("--p2").split(";")
    portList = [port1, port2]

    # For Linux API server only
    username = 'admin'
    password = 'admin'

    # For linux and connection_manager only. Set to True to leave the session alive for debugging.
    debugMode = False

    # Forcefully take port ownership if the portList are owned by other users.
    forceTakePortOwnership = True

    session = SessionAssistant(IpAddress=apiServerIp, RestPort=port, UserName=username, Password=password, 
                                SessionName=None, SessionId=None, ApiKey=None,
                                ClearConfig=True, LogLevel='info', LogFilename='restpy.log')

    ixNetwork = session.Ixnetwork
    ixNetwork.info('Assign ports')
    portMap = session.PortMapAssistant()
    vport = dict()
    for index,port in enumerate(portList):
        portName = 'Port_{}'.format(index+1)
        vport[portName] = portMap.Map(IpAddress=port[0], CardId=port[1], PortId=port[2], Name=portName)

    portMap.Connect(forceTakePortOwnership)


    ixNetwork.info('Creating Topology Group 1')
    topology1 = ixNetwork.Topology.add(Name='Topo1', Ports=vport['Port_1'])
    topology2 = ixNetwork.Topology.add(Name='Topo1', Ports=vport['Port_2'])

    #Configure rx_bgpd BGP
    deviceGroup1 = topology1.DeviceGroup.add(Name=tx_bgpd['Name'], Multiplier=1)
    ethernet1 = deviceGroup1.Ethernet.add(Name=tx_bgpd["Name"]+ "eth")
    ethernet1.Mac.Single(tx_bgpd["MAC"])

    ipv4 = ethernet1.Ipv4.add(Name=tx_bgpd["Name"] + "ipv4")
    ipv4.Address.Single(tx_bgpd["IPv4"])
    ipv4.GatewayIp.Single(rx_bgpd["IPv4"])

    ixNetwork.info('Configuring BgpIpv4Peer 1')
    bgp1 = ipv4.BgpIpv4Peer.add(Name='BGP Peer 1')
    bgp1.DutIp.Single(rx_bgpd["IPv4"])
    bgp1.Type.Single('external')
    bgp1.Enable4ByteAs.Single(True)
    bgp1.LocalAs4Bytes.Single(6000)

    ixNetwork.info('Configuring Network Group 2')
    networkGroup3 = deviceGroup1.NetworkGroup.add(Name=tx_bgpd["Name"] + "ipv4_rr", Multiplier='1')
    ipv4PrefixPool1 = networkGroup3.Ipv4PrefixPools.add(NumberOfAddresses='500')
    ipv4PrefixPool1.NetworkAddress.Increment(start_value=tx_bgpd["IPv4_routes"], step_value='0.0.1.0')
    ipv4PrefixPool1.PrefixLength.Single(24)

    #Configure tx_isis
    deviceGroup2 = topology1.DeviceGroup.add(Name='Device 2', Multiplier=1)
    ethernet2 = deviceGroup2.Ethernet.add(Name=tx_isisd["Name"]+ "eth")
    ethernet2.Mac.Single(tx_isisd["MAC"])

    ipv4 = ethernet2.Ipv4.add(Name=tx_isisd["Name"] + "ipv4")
    ipv4.Address.Single(tx_isisd["IPv4"])
    ipv4.GatewayIp.Single(rx_isisd["IPv4"])

    isis = ethernet2.IsisL3.add(Name="ISIS 17")

    ixNetwork.info('Configuring Network Group 3')
    networkGroup4 = deviceGroup2.NetworkGroup.add(Name=tx_isisd["Name"] + "ipv4_rr", Multiplier='1')
    ipv4PrefixPool2 = networkGroup4.Ipv4PrefixPools.add(NumberOfAddresses='500')
    ipv4PrefixPool2.NetworkAddress.Increment(start_value=tx_isisd["IPv4_routes"], step_value='0.0.1.0')
    ipv4PrefixPool2.PrefixLength.Single(24)


    #Configure rx_bgpd BGP
    deviceGroup3 = topology2.DeviceGroup.add(Name=rx_bgpd['Name'], Multiplier=1)
    ethernet1 = deviceGroup3.Ethernet.add(Name=rx_bgpd["Name"]+ "eth")
    ethernet1.Mac.Single(rx_bgpd["MAC"])

    ipv4 = ethernet1.Ipv4.add(Name=rx_bgpd["Name"] + "ipv4")
    ipv4.Address.Single(rx_bgpd["IPv4"])
    ipv4.GatewayIp.Single(tx_bgpd["IPv4"])

    ixNetwork.info('Configuring BgpIpv4Peer 1')
    bgp1 = ipv4.BgpIpv4Peer.add(Name='BGP Peer 1')
    bgp1.DutIp.Single(tx_bgpd["IPv4"])
    bgp1.Type.Single('external')
    bgp1.Enable4ByteAs.Single(True)
    bgp1.LocalAs4Bytes.Single(6500)

    ixNetwork.info('Configuring Network Group 5')
    networkGroup3 = deviceGroup3.NetworkGroup.add(Name=rx_bgpd["Name"] + "ipv4_rr", Multiplier='1')
    ipv4PrefixPool1a = networkGroup3.Ipv4PrefixPools.add(NumberOfAddresses='500')
    ipv4PrefixPool1a.NetworkAddress.Increment(start_value=rx_bgpd["IPv4_routes"], step_value='0.0.1.0')
    ipv4PrefixPool1a.PrefixLength.Single(24)

    #Configure rx_isis
    deviceGroup2 = topology2.DeviceGroup.add(Name=rx_isisd['Name'], Multiplier=1)
    ethernet2 = deviceGroup2.Ethernet.add(Name=rx_isisd["Name"]+ "eth")
    ethernet2.Mac.Single(rx_isisd["MAC"])

    ipv4 = ethernet2.Ipv4.add(Name=rx_isisd["Name"] + "ipv4")
    ipv4.Address.Single(rx_isisd["IPv4"])
    ipv4.GatewayIp.Single(tx_isisd["IPv4"])

    isis = ethernet2.IsisL3.add(Name="ISIS 17")

    ixNetwork.info('Configuring Network Group 6')
    networkGroup4 = deviceGroup2.NetworkGroup.add(Name=rx_isisd["Name"] + "ipv4_rr", Multiplier='1')
    ipv4PrefixPool2a = networkGroup4.Ipv4PrefixPools.add(NumberOfAddresses='500')
    ipv4PrefixPool2a.NetworkAddress.Increment(start_value=rx_isisd["IPv4_routes"], step_value='0.0.1.0')
    ipv4PrefixPool2a.PrefixLength.Single(24)



    ixNetwork.info('Create Traffic Item')
    trafficItem1 = ixNetwork.Traffic.TrafficItem.add(Name="BGP", BiDirectional=False, TrafficType='ipv4')
    ixNetwork.info('Add endpoint flow group')
    trafficItem1.EndpointSet.add(Sources=ipv4PrefixPool1, Destinations=ipv4PrefixPool1a)
    configElement = trafficItem1.ConfigElement.find()[0]
    configElement.FrameRate.update(Type='percentLineRate', Rate=1)
    configElement.FrameRateDistribution.PortDistribution = 'splitRateEvenly'
    configElement.FrameSize.FixedSize = 128
    configElement.TransmissionControl.update(Type='fixedFrameCount', FrameCount='1000')
    trafficItem1.Tracking.find()[0].TrackBy = ['flowGroup0']

    trafficItem2 = ixNetwork.Traffic.TrafficItem.add(Name="ISIS", BiDirectional=False, TrafficType='ipv4')
    ixNetwork.info('Add endpoint flow group')
    trafficItem2.EndpointSet.add(Sources=ipv4PrefixPool2, Destinations=ipv4PrefixPool2a)
    configElement = trafficItem2.ConfigElement.find()[0]
    configElement.FrameRate.update(Type='percentLineRate', Rate=1)
    configElement.FrameRateDistribution.PortDistribution = 'splitRateEvenly'
    configElement.FrameSize.FixedSize = 128
    configElement.TransmissionControl.update(Type='fixedFrameCount', FrameCount='1000')
    trafficItem2.Tracking.find()[0].TrackBy = ['flowGroup0']

    ixNetwork.StartAllProtocols(Arg1='sync')
    time.sleep(30)
    ixNetwork.info('Verify protocol sessions\n')
    protocolSummary = session.StatViewAssistant('Protocols Summary')
    protocolSummary.CheckCondition('Sessions Not Started', protocolSummary.EQUAL, 0)
    protocolSummary.CheckCondition('Sessions Down', protocolSummary.EQUAL, 0)
    ixNetwork.info(protocolSummary)

    trafficItem1.Generate()
    trafficItem2.Generate()

    ixNetwork.Traffic.Apply()
    ixNetwork.Traffic.StartStatelessTraffic()

    time.sleep(120)

    flowStatistics = session.StatViewAssistant('Flow Statistics')

    ixNetwork.info('{}\n'.format(flowStatistics))

    for rowNumber,flowStat in enumerate(flowStatistics.Rows):
        ixNetwork.info('\n\nSTATS: {}\n\n'.format(flowStat))
        ixNetwork.info('\nRow:{}  TxPort:{}  RxPort:{}  TxFrames:{}  RxFrames:{}\n'.format(
            rowNumber, flowStat['Tx Port'], flowStat['Rx Port'],
            flowStat['Tx Frames'], flowStat['Rx Frames']))

    ixNetwork.Traffic.StopStatelessTraffic()
    ixNetwork.StopAllProtocols(Arg1='sync')

