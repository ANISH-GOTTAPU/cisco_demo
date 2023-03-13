import time

from ixnetwork_restpy import *


def test_restpy():
    apiServerIp = '10.39.70.125'

    ixChassisIpList = ['10.39.64.137']
    portList = [[ixChassisIpList[0], 2,3], [ixChassisIpList[0], 2, 4]]

    # For Linux API server only
    username = 'admin'
    password = 'admin'

    # For linux and connection_manager only. Set to True to leave the session alive for debugging.
    debugMode = False

    # Forcefully take port ownership if the portList are owned by other users.
    forceTakePortOwnership = True

    session = SessionAssistant(IpAddress=apiServerIp, RestPort=443, UserName=username, Password=password, 
                                SessionName=None, SessionId=None, ApiKey=None,
                                ClearConfig=True, LogFilename='restpy.log')

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

    #Configuring Device 1
    deviceGroup1 = topology1.DeviceGroup.add(Name='Device 1', Multiplier=1)
    ethernet1 = deviceGroup1.Ethernet.add(Name='Ethernet 405')
    ethernet1.Mac.Single("00:10:94:00:01:91")
    ethernet1.EnableVlans.Single(True)
    ixNetwork.info('Configuring vlanID')
    vlanObj = ethernet1.Vlan.find()[0].VlanId.Single(1)

    ipv4 = ethernet1.Ipv4.add(Name='IPv4 35873')
    ipv4.Address.Single('166.1.1.2')
    ipv4.GatewayIp.Single('166.1.1.1')

    ipv6 = ethernet1.Ipv6.add(Name='IPv6 53932')
    ipv6.Address.Single('166:1:1::2')
    ipv6.GatewayIp.Single('166:1:1::1')

    ixNetwork.info('Configuring BgpIpv4Peer 1')
    bgp1 = ipv4.BgpIpv4Peer.add(Name='BGP Peer 1')
    bgp1.DutIp.Single('166.1.1.1')
    bgp1.Type.Single('external')
    bgp1.Enable4ByteAs.Single(True)
    bgp1.LocalAs4Bytes.Single(6550)

    isis = ethernet1.IsisL3.add(Name="ISIS 401")

    ixNetwork.info('Configuring Network Group 1')
    networkGroup1 = deviceGroup1.NetworkGroup.add(Name="BgpIpv4RouteConfig1", Multiplier='1')
    ipv4PrefixPool1 = networkGroup1.Ipv4PrefixPools.add(NumberOfAddresses='500')
    ipv4PrefixPool1.NetworkAddress.Increment(start_value='10.1.1.1', step_value='0.0.1.0')
    ipv4PrefixPool1.PrefixLength.Single(24)

    ixNetwork.info('Configuring Network Group 2')
    networkGroup2 = deviceGroup1.NetworkGroup.add(Name="BgpIpv6RouteConfig1", Multiplier='1')
    ipv6PrefixPool1 = networkGroup2.Ipv6PrefixPools.add(NumberOfAddresses='500')
    ipv6PrefixPool1.NetworkAddress.Single('10:1:1:1:1:1:1:1')
    ipv6PrefixPool1.PrefixLength.Single(64)

    ixNetwork.info('Configuring Network Group 3')
    networkGroup3 = deviceGroup1.NetworkGroup.add(Name="Ipv4IsisRouteConfig 1261", Multiplier='1')
    ipv4PrefixPool2 = networkGroup3.Ipv4PrefixPools.add(NumberOfAddresses='500')
    ipv4PrefixPool2.NetworkAddress.Increment(start_value='90.1.1.1', step_value='0.0.1.0')
    ipv4PrefixPool2.PrefixLength.Single(24)

    #Configure Device2 with ISIS
    deviceGroup2 = topology1.DeviceGroup.add(Name='Device 2', Multiplier=1)
    ethernet2 = deviceGroup2.Ethernet.add(Name='Ethernet 37')
    ethernet2.Mac.Single("00:10:94:00:01:AB")
    ethernet2.EnableVlans.Single(True)
    ixNetwork.info('Configuring vlanID')
    vlanObj = ethernet2.Vlan.find()[0].VlanId.Single(2)

    ipv4 = ethernet2.Ipv4.add(Name='IPv4 5854')
    ipv4.Address.Single('167.1.1.2')
    ipv4.GatewayIp.Single('167.1.1.1')

    isis = ethernet2.IsisL3.add(Name="ISIS 17")

    ixNetwork.info('Configuring Network Group 4')
    networkGroup4 = deviceGroup2.NetworkGroup.add(Name="Ipv4IsisRouteConfig 18", Multiplier='1')
    ipv4PrefixPool3 = networkGroup4.Ipv4PrefixPools.add(NumberOfAddresses='500')
    ipv4PrefixPool3.NetworkAddress.Increment(start_value='92.1.1.1', step_value='0.0.1.0')
    ipv4PrefixPool3.PrefixLength.Single(24)

    #Configure Device4 with v6 ISIS
    deviceGroup3 = topology1.DeviceGroup.add(Name='Device 4', Multiplier=1)
    ethernet3 = deviceGroup3.Ethernet.add(Name='Ethernet 60')
    ethernet3.Mac.Single("00:10:94:00:01:AC")
    ethernet3.EnableVlans.Single(True)
    ixNetwork.info('Configuring vlanID')
    vlanObj = ethernet3.Vlan.find()[0].VlanId.Single(3)

    ipv4 = ethernet3.Ipv4.add(Name='IPv4 3500')
    ipv4.Address.Single('170.1.1.2')
    ipv4.GatewayIp.Single('170.1.1.1')

    ipv6 = ethernet3.Ipv6.add(Name='IPv6 53932')
    ipv6.Address.Single('170:1:1::2')
    ipv6.GatewayIp.Single('170:1:1::1')

    isis = ethernet3.IsisL3.add(Name="ISIS 30")

    ixNetwork.info('Configuring Network Group 5')
    networkGroup5 = deviceGroup3.NetworkGroup.add(Name='Ipv6IsisRouteConfig 25', Multiplier='1')
    ipv6PrefixPool2 = networkGroup5.Ipv6PrefixPools.add(NumberOfAddresses='500')
    ipv6PrefixPool2.NetworkAddress.Single('90:1:1:1:1:1:1:1')
    ipv6PrefixPool2.PrefixLength.Single(64)

    ixNetwork.info('Creating Topology Group 1')
    topology2 = ixNetwork.Topology.add(Name='Topo2', Ports=vport['Port_2'])

    #Configuring Device 11
    deviceGroup4 = topology2.DeviceGroup.add(Name='Device 11', Multiplier=1)
    ethernet4 = deviceGroup4.Ethernet.add(Name='Ethernet 415')
    ethernet4.Mac.Single("00:10:94:00:01:9B")
    ethernet4.EnableVlans.Single(True)
    ixNetwork.info('Configuring vlanID')
    vlanObj = ethernet4.Vlan.find()[0].VlanId.Single(1)

    ipv4 = ethernet4.Ipv4.add(Name='IPv4 37206')
    ipv4.Address.Single('166.1.1.1')
    ipv4.GatewayIp.Single('166.1.1.2')

    ipv6 = ethernet4.Ipv6.add(Name='IPv6 56202')
    ipv6.Address.Single('166:1:1::1')
    ipv6.GatewayIp.Single('166:1:1::2')

    ixNetwork.info('Configuring BgpIpv4Peer 1')
    bgp1 = ipv4.BgpIpv4Peer.add(Name='BGP Peer 2')
    bgp1.DutIp.Single('166.1.1.2')
    bgp1.Type.Single('external')
    bgp1.Enable4ByteAs.Single(True)
    bgp1.LocalAs4Bytes.Single(6551)

    isis = ethernet4.IsisL3.add(Name="ISIS 411")

    ixNetwork.info('Configuring Network Group 1')
    networkGroup1a = deviceGroup4.NetworkGroup.add(Name="BgpIpv4RouteConfig1a", Multiplier='1')
    ipv4PrefixPool1a = networkGroup1a.Ipv4PrefixPools.add(NumberOfAddresses='500')
    ipv4PrefixPool1a.NetworkAddress.Increment(start_value='31.1.1.1', step_value='0.0.1.0')
    ipv4PrefixPool1a.PrefixLength.Single(32)

    ixNetwork.info('Configuring Network Group 2')
    networkGroup2a = deviceGroup4.NetworkGroup.add(Name="BgpIpv6RouteConfig1a", Multiplier='1')
    ipv6PrefixPool1a = networkGroup2a.Ipv6PrefixPools.add(NumberOfAddresses='500')
    ipv6PrefixPool1a.NetworkAddress.Single('11:1:1:1:1:1:1:1')
    ipv6PrefixPool1a.PrefixLength.Single(64)

    ixNetwork.info('Configuring Network Group 3')
    networkGroup3a = deviceGroup4.NetworkGroup.add(Name="Ipv4IsisRouteConfig 1261", Multiplier='1')
    ipv4PrefixPool2a = networkGroup3a.Ipv4PrefixPools.add(NumberOfAddresses='500')
    ipv4PrefixPool2a.NetworkAddress.Increment(start_value='91.1.1.1', step_value='0.0.1.0')
    ipv4PrefixPool2a.PrefixLength.Single(32)

    #Configure Device3 with ISIS
    deviceGroup5 = topology2.DeviceGroup.add(Name='Device 3', Multiplier=1)
    ethernet5 = deviceGroup5.Ethernet.add(Name='Ethernet 36')
    ethernet5.Mac.Single("00:10:94:00:01:AA")
    ethernet5.EnableVlans.Single(True)
    ixNetwork.info('Configuring vlanID')
    vlanObj = ethernet5.Vlan.find()[0].VlanId.Single(2)

    ipv4 = ethernet5.Ipv4.add(Name='IPv4 5631')
    ipv4.Address.Single('167.1.1.1')
    ipv4.GatewayIp.Single('167.1.1.2')

    isis = ethernet5.IsisL3.add(Name="ISIS 16")

    ixNetwork.info('Configuring Network Group 4')
    networkGroup4a = deviceGroup5.NetworkGroup.add(Name="Ipv4IsisRouteConfig 16", Multiplier='1')
    ipv4PrefixPool3a = networkGroup4a.Ipv4PrefixPools.add(NumberOfAddresses='500')
    ipv4PrefixPool3a.NetworkAddress.Increment(start_value='93.1.1.1', step_value='0.0.1.0')
    ipv4PrefixPool3a.PrefixLength.Single(32)

    #Configure Device5 with v6 ISIS
    deviceGroup6 = topology2.DeviceGroup.add(Name='Device 5', Multiplier=1)
    ethernet6 = deviceGroup6.Ethernet.add(Name='Ethernet 61')
    ethernet6.Mac.Single("00:10:94:00:01:AD")
    ethernet6.EnableVlans.Single(True)
    ixNetwork.info('Configuring vlanID')
    vlanObj = ethernet6.Vlan.find()[0].VlanId.Single(3)

    ipv4 = ethernet6.Ipv4.add(Name='IPv4 3501')
    ipv4.Address.Single('170.1.1.1')
    ipv4.GatewayIp.Single('170.1.1.2')

    ipv6 = ethernet6.Ipv6.add(Name='IPv6 2693')
    ipv6.Address.Single('170:1:1::1')
    ipv6.GatewayIp.Single('170:1:1::2')

    isis = ethernet6.IsisL3.add(Name="ISIS 31")

    ixNetwork.info('Configuring Network Group 5')
    networkGroup5a = deviceGroup6.NetworkGroup.add(Name='Ipv6IsisRouteConfig 25a', Multiplier='1')
    ipv6PrefixPool2a = networkGroup5a.Ipv6PrefixPools.add(NumberOfAddresses='500')
    ipv6PrefixPool2a.NetworkAddress.Single('91:1:1:1:1:1:1:1')
    ipv6PrefixPool2a.PrefixLength.Single(64)


    ixNetwork.info('Create Traffic Item')
    trafficItem1 = ixNetwork.Traffic.TrafficItem.add(Name="IPv4_BGP_UUT1_PEER1-4", BiDirectional=False, TrafficType='ipv4')
    ixNetwork.info('Add endpoint flow group')
    trafficItem1.EndpointSet.add(Sources=ipv4PrefixPool1, Destinations=ipv4PrefixPool1a)
    configElement = trafficItem1.ConfigElement.find()[0]
    configElement.FrameRate.update(Type='percentLineRate', Rate=1)
    configElement.FrameRateDistribution.PortDistribution = 'splitRateEvenly'
    configElement.FrameSize.FixedSize = 128
    trafficItem1.Tracking.find()[0].TrackBy = ['flowGroup0']

    trafficItem2 = ixNetwork.Traffic.TrafficItem.add(Name="IPv4_ISIS_UUT1_PEER1-2", BiDirectional=False, TrafficType='ipv4')
    ixNetwork.info('Add endpoint flow group')
    trafficItem2.EndpointSet.add(Sources=ipv4PrefixPool2, Destinations=ipv4PrefixPool2a)
    configElement = trafficItem2.ConfigElement.find()[0]
    configElement.FrameRate.update(Type='percentLineRate', Rate=1)
    configElement.FrameRateDistribution.PortDistribution = 'splitRateEvenly'
    configElement.FrameSize.FixedSize = 128
    trafficItem2.Tracking.find()[0].TrackBy = ['flowGroup0']

    trafficItem3 = ixNetwork.Traffic.TrafficItem.add(Name="IPv6_BGP_UUT1_PEER1-2", BiDirectional=False, TrafficType='ipv6')
    ixNetwork.info('Add endpoint flow group')
    trafficItem3.EndpointSet.add(Sources=ipv6PrefixPool1, Destinations=ipv6PrefixPool1a)
    configElement = trafficItem3.ConfigElement.find()[0]
    configElement.FrameRate.update(Type='percentLineRate', Rate=1)
    configElement.FrameRateDistribution.PortDistribution = 'splitRateEvenly'
    configElement.FrameSize.FixedSize = 128
    trafficItem3.Tracking.find()[0].TrackBy = ['flowGroup0']

    trafficItem4 = ixNetwork.Traffic.TrafficItem.add(Name="IPv4_BGP_PEER1_UUT1-2", BiDirectional=False, TrafficType='ipv4')
    ixNetwork.info('Add endpoint flow group')
    trafficItem4.EndpointSet.add(Sources=ipv4PrefixPool1a, Destinations=ipv4PrefixPool1)
    configElement = trafficItem4.ConfigElement.find()[0]
    configElement.FrameRate.update(Type='percentLineRate', Rate=1)
    configElement.FrameRateDistribution.PortDistribution = 'splitRateEvenly'
    configElement.FrameSize.FixedSize = 128
    trafficItem4.Tracking.find()[0].TrackBy = ['flowGroup0']

    trafficItem5 = ixNetwork.Traffic.TrafficItem.add(Name="IPv4_ISIS_PEER1_UUT1-2", BiDirectional=False, TrafficType='ipv4')
    ixNetwork.info('Add endpoint flow group')
    trafficItem5.EndpointSet.add(Sources=ipv4PrefixPool2a, Destinations=ipv4PrefixPool2)
    configElement = trafficItem5.ConfigElement.find()[0]
    configElement.FrameRate.update(Type='percentLineRate', Rate=1)
    configElement.FrameRateDistribution.PortDistribution = 'splitRateEvenly'
    configElement.FrameSize.FixedSize = 128
    trafficItem5.Tracking.find()[0].TrackBy = ['flowGroup0']

    trafficItem6 = ixNetwork.Traffic.TrafficItem.add(Name="IPv6_BGP_PEER1_UUT1-2", BiDirectional=False, TrafficType='ipv6')
    ixNetwork.info('Add endpoint flow group')
    trafficItem6.EndpointSet.add(Sources=ipv6PrefixPool1a, Destinations=ipv6PrefixPool1)
    configElement = trafficItem6.ConfigElement.find()[0]
    configElement.FrameRate.update(Type='percentLineRate', Rate=1)
    configElement.FrameRateDistribution.PortDistribution = 'splitRateEvenly'
    configElement.FrameSize.FixedSize = 128
    trafficItem6.Tracking.find()[0].TrackBy = ['flowGroup0']

    trafficItem7 = ixNetwork.Traffic.TrafficItem.add(Name="IPv6_ISIS_UUT1_PEER1-3", BiDirectional=False, TrafficType='ipv6')
    ixNetwork.info('Add endpoint flow group')
    trafficItem7.EndpointSet.add(Sources=ipv6PrefixPool2, Destinations=ipv6PrefixPool2a)
    configElement = trafficItem7.ConfigElement.find()[0]
    configElement.FrameRate.update(Type='percentLineRate', Rate=1)
    configElement.FrameRateDistribution.PortDistribution = 'splitRateEvenly'
    configElement.FrameSize.FixedSize = 128
    trafficItem7.Tracking.find()[0].TrackBy = ['flowGroup0']

    trafficItem8 = ixNetwork.Traffic.TrafficItem.add(Name="IPv6_ISIS_PEER1_UUT1-2", BiDirectional=False, TrafficType='ipv6')
    ixNetwork.info('Add endpoint flow group')
    trafficItem8.EndpointSet.add(Sources=ipv6PrefixPool2a, Destinations=ipv6PrefixPool2)
    configElement = trafficItem8.ConfigElement.find()[0]
    configElement.FrameRate.update(Type='percentLineRate', Rate=1)
    configElement.FrameRateDistribution.PortDistribution = 'splitRateEvenly'
    configElement.FrameSize.FixedSize = 128
    trafficItem8.Tracking.find()[0].TrackBy = ['flowGroup0']

    ixNetwork.StartAllProtocols(Arg1='sync')
    time.sleep(30)
    ixNetwork.info('Verify protocol sessions\n')
    protocolSummary = session.StatViewAssistant('Protocols Summary')
    protocolSummary.CheckCondition('Sessions Not Started', protocolSummary.EQUAL, 0)
    protocolSummary.CheckCondition('Sessions Down', protocolSummary.EQUAL, 0)
    ixNetwork.info(protocolSummary)

    trafficItem1.Generate()
    trafficItem2.Generate()
    trafficItem3.Generate()
    trafficItem4.Generate()
    trafficItem5.Generate()
    trafficItem6.Generate()
    trafficItem7.Generate()
    trafficItem8.Generate()

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

