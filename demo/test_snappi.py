import logging as log
import pytest
import snappi
import time
import datetime

def test_snappi():

    api = snappi.api(
            "localhost:40051",
            verify=False,
            transport="grpc"
        )
    config = api.config()

    p1 = config.ports.port(name='p1', location="10.39.64.137;2;1")[-1]
    p2 = config.ports.port(name='p2', location="10.39.64.137;2;2")[-1]
    
    config.options.port_options.location_preemption = True
    
    d1 = config.devices.device(name='Device 1')[-1]
    d2 = config.devices.device(name='Device 2')[-1]
    d4 = config.devices.device(name='Device 4')[-1]
    
    d11 = config.devices.device(name='Device 11')[-1]
    d3 = config.devices.device(name='Device 3')[-1]
    d5 = config.devices.device(name='Device 5')[-1]
    
    #Configure Device1 with ISIS and BGP
    eth = d1.ethernets.add()
    eth.port_name = p1.name
    eth.name = 'Ethernet 405'
    eth.mac = "00:10:94:00:01:91"
    vlan = eth.vlans.add()
    vlan.name = 'vlan1'
    vlan.id = 1
    ipv4 = eth.ipv4_addresses.add()
    ipv4.name = 'IPv4 35873'
    ipv4.address = '166.1.1.2'
    ipv4.gateway = '166.1.1.1'
    ipv4.prefix = 24
    
    ipv6 = eth.ipv6_addresses.add()
    ipv6.name = 'IPv6 53932'
    ipv6.address = '166:1:1::2'
    ipv6.gateway = '166:1:1::1'
    ipv6.prefix = 64
    
    bgpv4 = d1.bgp
    bgpv4.router_id = '192.0.1.145'
    bgpv4_int = bgpv4.ipv4_interfaces.add()
    bgpv4_int.ipv4_name = ipv4.name
    bgpv4_peer = bgpv4_int.peers.add()
    bgpv4_peer.name = 'BGP Peer 1' 
    bgpv4_peer.as_type = "ebgp"
    bgpv4_peer.peer_address = '166.1.1.1'
    bgpv4_peer.as_number = 6550
    
    route_range = bgpv4_peer.v4_routes.add(name="BgpIpv4RouteConfig1") 
    route_range.addresses.add(address='10.1.1.1', prefix=24, count=500)
    
    route_rangev6 = bgpv4_peer.v6_routes.add(name="BgpIpv6RouteConfig1") 
    route_rangev6.addresses.add(address='10:1:1:1:1:1:1:1', prefix=64, count=500)
    
    isis = d1.isis
    isis.name = "isis 401"
    isis.system_id = "9001"
    isis_int = isis.interfaces.add()
    isis_int.name = "isis Intf 1"
    isis_int.eth_name = eth.name
    isis_int.network_type = 'broadcast'
    route_range = isis.v4_routes.add(name='Ipv4IsisRouteConfig 1261')
    route_range.addresses.add(address='90.1.1.1', prefix=24, count=500)
    
    #Configure Device2 with ISIS and BGP
    eth = d2.ethernets.add()
    eth.port_name = p1.name
    eth.name = 'Ethernet 37'
    eth.mac = "00:10:94:00:01:AB"
    
    vlan = eth.vlans.add()
    vlan.name = 'vlan2'
    vlan.id = 2
    ipv4 = eth.ipv4_addresses.add()
    ipv4.name = 'IPv4 5854'
    ipv4.address = '167.1.1.2'
    ipv4.gateway = '167.1.1.1'
    ipv4.prefix = 24
    
    isis = d2.isis
    isis.name = "isis 17"
    isis.system_id = "9001"
    isis_int = isis.interfaces.add()
    isis_int.name = "isis Intf 2"
    isis_int.eth_name = eth.name
    isis_int.network_type = 'broadcast'
    route_range = isis.v4_routes.add(name='Ipv4IsisRouteConfig 18')
    route_range.addresses.add(address='92.1.1.1', prefix=24, count=500)
    
    #Configure Device4 with ISIS and BGP
    eth = d4.ethernets.add()
    eth.port_name = p1.name
    eth.name = 'Ethernet 60'
    eth.mac = "00:10:94:00:01:AC"
    
    vlan = eth.vlans.add()
    vlan.name = 'vlan3'
    vlan.id = 3
    ipv4 = eth.ipv4_addresses.add()
    ipv4.name = 'IPv4 3500'
    ipv4.address = '170.1.1.2'
    ipv4.gateway = '170.1.1.1'
    ipv4.prefix = 24
    
    ipv6 = eth.ipv6_addresses.add()
    ipv6.name = 'IPv6 2684'
    ipv6.address = '170:1:1::2'
    ipv6.gateway = '170:1:1::1'
    ipv6.prefix = 64
    
    isis = d4.isis
    isis.name = "isis 30"
    isis.system_id = "9001"
    isis_int = isis.interfaces.add()
    isis_int.name = "isis Intf 3"
    isis_int.eth_name = eth.name
    isis_int.network_type = 'broadcast'
    route_rangev6 = isis.v6_routes.add(name='Ipv6IsisRouteConfig 25')
    route_rangev6.addresses.add(address='90:1:1:1:1:1:1:1', prefix=64, count=500)
    
    
    #Configure Device11 with ISIS and BGP
    eth = d11.ethernets.add()
    eth.port_name = p2.name
    eth.name = 'Ethernet 415'
    eth.mac = "00:10:94:00:01:9B"
    vlan = eth.vlans.add()
    vlan.name = 'vlan415'
    vlan.id = 1
    
    ipv4 = eth.ipv4_addresses.add()
    ipv4.name = 'IPv4 37206'
    ipv4.address = '166.1.1.1'
    ipv4.gateway = '166.1.1.2'
    ipv4.prefix = 24
    
    ipv6 = eth.ipv6_addresses.add()
    ipv6.name = 'IPv6 56202'
    ipv6.address = '166:1:1::1'
    ipv6.gateway = '166:1:1::2'
    ipv6.prefix = 64
    
    bgpv4 = d11.bgp
    bgpv4.router_id = '192.0.1.155'
    bgpv4_int = bgpv4.ipv4_interfaces.add()
    bgpv4_int.ipv4_name = ipv4.name
    bgpv4_peer = bgpv4_int.peers.add()
    bgpv4_peer.name = 'BGP Peer2' 
    bgpv4_peer.as_type = "ebgp"
    bgpv4_peer.peer_address = '166.1.1.2'
    bgpv4_peer.as_number = 6551
    
    route_range = bgpv4_peer.v4_routes.add(name="BgpIpv4RouteConfig1a") 
    route_range.addresses.add(address='31.1.1.1', prefix=32, count=500)
    
    route_rangev6 = bgpv4_peer.v6_routes.add(name="BgpIpv6RouteConfig1a") 
    route_rangev6.addresses.add(address='11:1:1:1:1:1:1:1', prefix=64, count=500)
    
    isis = d11.isis
    isis.name = "ISIS 411"
    isis.system_id = "9001"
    isis_int = isis.interfaces.add()
    isis_int.name = "isis Intf 1a"
    isis_int.eth_name = eth.name
    isis_int.network_type = 'broadcast'
    route_range = isis.v4_routes.add(name='Ipv4IsisRouteConfig 1262')
    route_range.addresses.add(address='91.1.1.1', prefix=32, count=500)
    
    
    eth = d3.ethernets.add()
    eth.port_name = p2.name
    eth.name = 'Ethernet 36'
    eth.mac = "00:10:94:00:01:AA"
    
    vlan = eth.vlans.add()
    vlan.name = 'vlan2a'
    vlan.id = 2
    ipv4 = eth.ipv4_addresses.add()
    ipv4.name = 'IPv4 5631'
    ipv4.address = '167.1.1.1'
    ipv4.gateway = '167.1.1.2'
    ipv4.prefix = 24
    
    isis = d3.isis
    isis.name = "ISIS 16"
    isis.system_id = "9001"
    isis_int = isis.interfaces.add()
    isis_int.name = "isis Intf 2a"
    isis_int.eth_name = eth.name
    isis_int.network_type = 'broadcast'
    route_range = isis.v4_routes.add(name='Ipv4IsisRouteConfig 16')
    route_range.addresses.add(address='93.1.1.1', prefix=32, count=500)
    
    eth = d5.ethernets.add()
    eth.port_name = p2.name
    eth.name = 'Ethernet 61'
    eth.mac = "00:10:94:00:01:AD"
    
    vlan = eth.vlans.add()
    vlan.name = 'vlan3a'
    vlan.id = 3
    ipv4 = eth.ipv4_addresses.add()
    ipv4.name = 'IPv4 3501'
    ipv4.address = '170.1.1.1'
    ipv4.gateway = '170.1.1.2'
    ipv4.prefix = 24
    
    ipv6 = eth.ipv6_addresses.add()
    ipv6.name = 'IPv6 2693'
    ipv6.address = '170:1:1::1'
    ipv6.gateway = '170:1:1::2'
    ipv6.prefix = 64
    
    isis = d5.isis
    isis.name = "isis 31"
    isis.system_id = "9001"
    isis_int = isis.interfaces.add()
    isis_int.name = "isis Intf 3a"
    isis_int.eth_name = eth.name
    isis_int.network_type = 'broadcast'
    route_rangev6 = isis.v6_routes.add(name='Network_Group5a')
    route_rangev6.addresses.add(address='91:1:1:1:1:1:1:1', prefix=64, count=500)
    
    
    
    #flow1
    f1 = config.flows.flow(name="IPv4_BGP_UUT1_PEER1-4")[-1]
    f1.tx_rx.port.tx_name = p1.name
    f1.tx_rx.port.rx_name = p2.name
    f1.rate.percentage = 1
    f1.metrics.enable = True
    
    eth, vlan, mpls, ip = (f1.packet.ethernet().vlan().mpls().ipv4())
    eth.src.value = "00:10:94:00:01:91"
    eth.dst.value = "00:10:94:00:01:9B"
    
    vlan.id.value = 1
    mpls.label.value = 16
    
    ip.src.increment.start = '10.1.1.1'
    ip.src.increment.step = '0.0.1.0'
    ip.src.increment.count = 500
    
    ip.dst.increment.start = '31.1.1.1'
    ip.dst.increment.step = '0.0.0.1'
    ip.dst.increment.count = 500
    
    #IPv4_ISIS_UUT1_PEER1-2
    f2 = config.flows.flow(name="IPv4_ISIS_UUT1_PEER1-2")[-1]
    f2.tx_rx.port.tx_name = p1.name
    f2.tx_rx.port.rx_name = p2.name
    f2.rate.percentage = 1
    f2.metrics.enable = True
    
    eth, vlan, mpls, ip = (f2.packet.ethernet().vlan().mpls().ipv4())
    eth.src.value = "00:10:94:00:01:91"
    eth.dst.value = "00:10:94:00:01:9B"
    
    
    vlan.id.value = 1
    mpls.label.value = 16
    
    ip.src.increment.start = '90.1.1.1'
    ip.src.increment.step = '0.0.1.0'
    ip.src.increment.count = 500
    
    ip.dst.increment.start = '91.1.1.1'
    ip.dst.increment.step = '0.0.0.1'
    ip.dst.increment.count = 500
    
    #IPv6_BGP_UUT1_PEER1-2
    f3 = config.flows.flow(name="IPv6_BGP_UUT1_PEER1-2")[-1]
    f3.tx_rx.port.tx_name = p1.name
    f3.tx_rx.port.rx_name = p2.name
    f3.rate.percentage = 1
    f3.metrics.enable = True
    
    eth, vlan, mpls, ipv6 = (f3.packet.ethernet().vlan().mpls().ipv6())
    eth.src.value = "00:10:94:00:01:91"
    eth.dst.value = "00:10:94:00:01:9B"
    
    
    vlan.id.value = 1
    mpls.label.value = 16
    
    ipv6.src.increment.start = '10:1:1:1:1:1:1:1'
    ipv6.src.increment.step = '0:0:0:1:0:0:0:0'
    ipv6.src.increment.count = 500
    
    ipv6.dst.increment.start = '11:1:1:1:1:1:1:1'
    ipv6.dst.increment.step = '0:0:0:1:0:0:0:0'
    ipv6.dst.increment.count = 500
    
    #IPv4_BGP_PEER1_UUT1-2
    f4 = config.flows.flow(name="IPv4_BGP_PEER1_UUT1-2")[-1]
    f4.tx_rx.port.tx_name = p2.name
    f4.tx_rx.port.rx_name = p1.name
    f4.rate.percentage = 1
    f4.metrics.enable = True
    
    eth, vlan, mpls, ip = (f4.packet.ethernet().vlan().mpls().ipv4())
    eth.src.value = "00:10:94:00:01:9B"
    eth.dst.value = "00:10:94:00:01:91"
    
    vlan.id.value = 1
    mpls.label.value = 16
    
    ip.src.increment.start = '31.1.1.1'
    ip.src.increment.step = '0.0.0.1'
    ip.src.increment.count = 500
    
    ip.dst.increment.start = '10.1.1.1'
    ip.dst.increment.step = '0.0.1.0'
    ip.dst.increment.count = 500
    
    #IPv4_ISIS_PEER1_UUT1-2
    f5 = config.flows.flow(name="IPv4_ISIS_PEER1_UUT1-2")[-1]
    f5.tx_rx.port.tx_name = p2.name
    f5.tx_rx.port.rx_name = p1.name
    f5.rate.percentage = 1
    f5.metrics.enable = True
    
    eth, vlan, mpls, ip = (f5.packet.ethernet().vlan().mpls().ipv4())
    eth.src.value = "00:10:94:00:01:9B"
    eth.dst.value = "00:10:94:00:01:91"
    
    
    vlan.id.value = 1
    mpls.label.value = 16
    
    ip.src.increment.start = '91.1.1.1'
    ip.src.increment.step = '0.0.0.1'
    ip.src.increment.count = 500
    
    ip.dst.increment.start = '90.1.1.1'
    ip.dst.increment.step = '0.0.1.0'
    ip.dst.increment.count = 500
    
    #IPv6_BGP_UUT1_PEER1-2
    f6 = config.flows.flow(name="IPv6_BGP_PEER1_UUT1-2")[-1]
    f6.tx_rx.port.tx_name = p2.name
    f6.tx_rx.port.rx_name = p1.name
    f6.rate.percentage = 1
    f6.metrics.enable = True
    
    eth, vlan, mpls, ipv6 = (f6.packet.ethernet().vlan().mpls().ipv6())
    eth.src.value = "00:10:94:00:01:9B"
    eth.dst.value = "00:10:94:00:01:91"
    
    
    vlan.id.value = 1
    mpls.label.value = 16
    
    ipv6.src.increment.start = '11:1:1:1:1:1:1:1'
    ipv6.src.increment.step = '0:0:0:1:0:0:0:0'
    ipv6.src.increment.count = 500
    
    ipv6.dst.increment.start = '10:1:1:1:1:1:1:1'
    ipv6.dst.increment.step = '0:0:0:1:0:0:0:0'
    ipv6.dst.increment.count = 500
    
    #IPv6_ISIS_UUT1_PEER1-3
    f7 = config.flows.flow(name="IPv6_ISIS_UUT1_PEER1-3")[-1]
    f7.tx_rx.port.tx_name = p1.name
    f7.tx_rx.port.rx_name = p2.name
    f7.rate.percentage = 1
    f7.metrics.enable = True
    
    eth, vlan, ipv6 = (f7.packet.ethernet().vlan().ipv6())
    eth.src.value = "00:10:94:00:01:AC"
    eth.dst.value = "00:10:94:00:01:AD"
    
    
    vlan.id.value = 3
    
    ipv6.src.increment.start = '90:1:1:1:1:1:1:1'
    ipv6.src.increment.step = '0:0:0:1:0:0:0:0'
    ipv6.src.increment.count = 500
    
    ipv6.dst.increment.start = '91:1:1:1:1:1:1:1'
    ipv6.dst.increment.step = '0:0:0:1:0:0:0:0'
    ipv6.dst.increment.count = 500
    
    #IPv6_ISIS_PEER1_UUT1-2
    f8 = config.flows.flow(name="IPv6_ISIS_PEER1_UUT1-2")[-1]
    f8.tx_rx.port.tx_name = p2.name
    f8.tx_rx.port.rx_name = p1.name
    f8.rate.percentage = 1
    f8.metrics.enable = True
    
    eth, vlan, ipv6 = (f8.packet.ethernet().vlan().ipv6())
    eth.src.value = "00:10:94:00:01:AD"
    eth.dst.value = "00:10:94:00:01:AC"
    
    vlan.id.value = 3
    
    ipv6.src.increment.start = '91:1:1:1:1:1:1:1'
    ipv6.src.increment.step = '0:0:0:1:0:0:0:0'
    ipv6.src.increment.count = 500
    
    ipv6.dst.increment.start = '90:1:1:1:1:1:1:1'
    ipv6.dst.increment.step = '0:0:0:1:0:0:0:0'
    ipv6.dst.increment.count = 500
    
    api.set_config(config)

    time.sleep(10)
    ps = api.protocol_state()
    ps.state = ps.START
    api.set_protocol_state(ps)

    time.sleep(10)
    ts = api.transmit_state()
    ts.state = ts.START
    api.set_transmit_state(ts)

    time.sleep(10)
    # wait_for(
    #     fn=lambda: flow_metrics_ok(api), fn_name="wait_for_flow_metrics"
    # )

    time.sleep(10)
    ts = api.transmit_state()
    ts.state = ts.STOP
    api.set_transmit_state(ts)

    req = api.metrics_request()
    req.flow.flow_names = []

    metrics = api.get_metrics(req).flow_metrics

    print(metrics)

def flow_metrics_ok(api):
    for m in api.get_flow_metrics():
        if (
            m.frames_tx <= 10000 
            or m.frames_rx <= 10000
        ):
            return False
    return True


def wait_for(
    fn, fn_name="wait_for", interval_seconds=0.5, timeout_seconds=10
):
    start = datetime.datetime.now()
    try:
        log.info("Waiting for %s ...", fn_name)
        while True:
            if fn():
                log.info("Done waiting for %s", fn_name)
                return

            elapsed = datetime.datetime.now() - start
            if elapsed.seconds > timeout_seconds:
                msg = "timeout occurred while waiting for %s" % fn_name
                raise Exception(msg)

            time.sleep(interval_seconds)
    finally:
        timer(fn_name, start)

def timer(fn_name, since):
    elapsed = (datetime.datetime.now() - since).microseconds * 1000
    log.info("Elapsed duration %s: %d ns", fn_name, elapsed)


def get_flow_metrics(api):
    start = datetime.datetime.now()
    try:
        log.info("Getting flow metrics ...")
        req = api.metrics_request()
        req.flow.flow_names = []

        metrics = api.get_metrics(req).flow_metrics

        # tb = table.Table(
        #     "Flow Metrics",
        #     [
        #         "Name",
        #         "State",
        #         "Frames Tx",
        #         "Frames Rx",
        #         "FPS Tx",
        #         "FPS Rx",
        #         "Bytes Tx",
        #         "Bytes Rx",
        #     ],
        # )

        # for m in metrics:
        #     tb.append_row(
        #         [
        #             m.name,
        #             m.transmit,
        #             m.frames_tx,
        #             m.frames_rx,
        #             m.frames_tx_rate,
        #             m.frames_rx_rate,
        #             m.bytes_tx,
        #             m.bytes_rx,
        #         ]
        #     )

        # log.info(tb)
        return metrics
    finally:
        timer("get_flow_metrics", start)
