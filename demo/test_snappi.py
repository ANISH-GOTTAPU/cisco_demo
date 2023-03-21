import logging as log
import pytest
import snappi
import time
import datetime
from table import table

def test_snappi(request):

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
        "IPv4_routes": "40.1.1.1",
    }

    api = snappi.api(
            request.config.getoption("--host"),
            verify=False,
            transport="grpc"
        )
    config = api.config()

    port1 = config.ports.add(name='p1', location=request.config.getoption("--p1"))
    port2 = config.ports.add(name='p2', location=request.config.getoption("--p2"))
    
    config.options.port_options.location_preemption = True
    
    txd1 = config.devices.add(name=tx_bgpd["Name"])
    txd2 = config.devices.add(name=tx_isisd["Name"])
    
    rxd1 = config.devices.add(name=rx_bgpd["Name"])
    rxd2 = config.devices.add(name=rx_isisd["Name"])
    
    #Configure tx_bgpd BGP
    tx_bgpd_eth = txd1.ethernets.add(name=tx_bgpd["Name"]+ "eth")
    tx_bgpd_eth.connection.set(port_name=port1.name)
    tx_bgpd_eth.set(mac=tx_bgpd["MAC"], mtu=1500)

    tx_bgpd_ip = tx_bgpd_eth.ipv4_addresses.add(name=tx_bgpd["Name"] + "ipv4")
    tx_bgpd_ip.set(address=tx_bgpd["IPv4"], gateway=rx_bgpd["IPv4"], prefix=24)
    
    txd1.bgp.router_id = tx_bgpd["IPv4"]

    tx_bgpd_bgpv4 = txd1.bgp.ipv4_interfaces.add(ipv4_name=tx_bgpd_ip.name)

    tx_bgpd_bgpv4_peer = tx_bgpd_bgpv4.peers.add(name='BGP Peer 1')
    tx_bgpd_bgpv4_peer.set(as_number=6000, as_type="ebgp", peer_address=rx_bgpd["IPv4"])

    tx_bgpd_bgpv4_peer.learned_information_filter.set(
        unicast_ipv4_prefix=True, unicast_ipv6_prefix=True
    )
    
    tx_bgpd_bgpv4_peer_rrv4 = tx_bgpd_bgpv4_peer.v4_routes.add(name=tx_bgpd["Name"] + "ipv4_rr") 
    tx_bgpd_bgpv4_peer_rrv4.addresses.add(address=tx_bgpd["IPv4_routes"], prefix=24, count=500)
    
    tx_bgpd_bgpv4_peer_rrv6 = tx_bgpd_bgpv4_peer.v6_routes.add(name=tx_bgpd["Name"] + "ipv6_rr") 
    tx_bgpd_bgpv4_peer_rrv6.addresses.add(address=tx_bgpd["IPv6_routes"], prefix=64, count=500)


    #Configure rx_bgpd BGP
    rx_bgpd_eth = rxd1.ethernets.add(name=rx_bgpd["Name"] + "eth")
    rx_bgpd_eth.set(mac=rx_bgpd["MAC"], mtu=1500)
    rx_bgpd_eth.connection.set(port_name=port2.name)

    rx_bgpd_ip = rx_bgpd_eth.ipv4_addresses.add(name=rx_bgpd["Name"] + "ipv4")
    rx_bgpd_ip.set(address=rx_bgpd["IPv4"], gateway=tx_bgpd["IPv4"], prefix=24)
    
    rxd1.bgp.router_id = rx_bgpd["IPv4"]

    rx_bgpd_bgpv4 = rxd1.bgp.ipv4_interfaces.add(ipv4_name=rx_bgpd_ip.name)

    rx_bgpd_bgpv4_peer = rx_bgpd_bgpv4.peers.add(name='BGP Peer 2')
    rx_bgpd_bgpv4_peer.set(as_number=6000, as_type="ebgp", peer_address=tx_bgpd["IPv4"])

    rx_bgpd_bgpv4_peer.learned_information_filter.set(
        unicast_ipv4_prefix=True, unicast_ipv6_prefix=True
    )
    
    rx_bgpd_bgpv4_peer_rrv4 = rx_bgpd_bgpv4_peer.v4_routes.add(name=rx_bgpd["Name"] + "ipv4_rr") 
    rx_bgpd_bgpv4_peer_rrv4.addresses.add(address=rx_bgpd["IPv4_routes"], prefix=24, count=500)
    
    rx_bgpd_bgpv4_peer_rrv6 = rx_bgpd_bgpv4_peer.v6_routes.add(name=rx_bgpd["Name"] + "ipv6_rr") 
    rx_bgpd_bgpv4_peer_rrv6.addresses.add(address=rx_bgpd["IPv6_routes"], prefix=64, count=500)


    ftx_v4  = config.flows.flow(name="BGP")[-1]
    ftx_v4.tx_rx.device.set(tx_names=[tx_bgpd_bgpv4_peer_rrv4.name], rx_names=[rx_bgpd_bgpv4_peer_rrv4.name])
    ftx_v4.rate.pps = 100
    ftx_v4.duration.fixed_packets.packets = 1000
    ftx_v4.size.fixed = 128
    ftx_v4.metrics.enable = True

    ftx_v4_eth, ftx_v4_ip, ftx_v4_tcp = ftx_v4.packet.ethernet().ipv4().tcp()
    ftx_v4_eth.src.value = tx_bgpd["MAC"]
    ftx_v4_ip.src.value = tx_bgpd["IPv4"]
    ftx_v4_ip.dst.value = rx_bgpd["IPv4"]
    ftx_v4_tcp.src_port.value = 5000
    ftx_v4_tcp.dst_port.value = 6000
    
    #Configure tx_isis
    tx_isisd_eth = txd2.ethernets.add(name=tx_isisd["Name"]+ "eth")
    tx_isisd_eth.set(mac=tx_isisd["MAC"], mtu=1500)
    tx_isisd_eth.connection.set(port_name=port1.name)

    tx_isisd_ip = tx_isisd_eth.ipv4_addresses.add(name=tx_isisd["Name"] + "ipv4")
    tx_isisd_ip.set(address=tx_isisd["IPv4"], gateway=rx_isisd["IPv4"], prefix=24)
    
    txd2.isis.name = "tx_isis"
    txd2.isis.system_id = "640000000001"

    tx_isisd_isis = txd2.isis.interfaces.add(eth_name=tx_isisd_eth.name)
    tx_isisd_isis.set(name="tx_isisd_isis_int", network_type='broadcast',level_type="level_2")

    tx_isisd_rrv4 = txd2.isis.v4_routes.add(name=tx_isisd["Name"] + "ipv4_rr")
    tx_isisd_rrv4.addresses.add(address=tx_isisd["IPv4_routes"], prefix=24, count=500)


    #Configure rx_isis
    rx_isisd_eth = rxd2.ethernets.add(name=rx_isisd["Name"]+ "eth")
    rx_isisd_eth.set(mac=rx_isisd["MAC"], mtu=1500)
    rx_isisd_eth.connection.set(port_name=port2.name)

    rx_isisd_ip = rx_isisd_eth.ipv4_addresses.add(name=rx_isisd["Name"] + "ipv4")
    rx_isisd_ip.set(address=rx_isisd["IPv4"], gateway=tx_isisd["IPv4"], prefix=24)
    
    rxd2.isis.name = "rx_isis"
    rxd2.isis.system_id = "640000000002"

    rx_isisd_isis = rxd2.isis.interfaces.add(eth_name=rx_isisd_eth.name)
    rx_isisd_isis.set(name="rx_isisd_isis_int", network_type='broadcast',level_type="level_2")

    rx_isisd_rrv4 = rxd2.isis.v4_routes.add(name=rx_isisd["Name"] + "ipv4_rr")
    rx_isisd_rrv4.addresses.add(address=rx_isisd["IPv4_routes"], prefix=24, count=500)


    f2  = config.flows.flow(name="ISIS")[-1]
    f2.tx_rx.device.set(tx_names=[tx_isisd_rrv4.name], rx_names=[rx_isisd_rrv4.name])
    f2.rate.pps = 100
    f2.duration.fixed_packets.packets = 1000
    f2.size.fixed = 128
    f2.metrics.enable = True

    f2_eth, f2_ip, f2_tcp = f2.packet.ethernet().ipv4().tcp()
    f2_eth.src.value = tx_bgpd["MAC"]
    f2_ip.src.value = tx_bgpd["IPv4"]
    f2_ip.dst.value = rx_bgpd["IPv4"]
    f2_tcp.src_port.value = 5000
    f2_tcp.dst_port.value = 6000

    log.info("Setting Config")
    api.set_config(config)

    time.sleep(20)
    log.info("Starting Protocols")
    ps = api.protocol_state()
    ps.state = ps.START
    api.set_protocol_state(ps)

    time.sleep(20)
    wait_for(
        fn=lambda: arp_ok(api), fn_name="wait_for_arp"
    )

    log.info("Starting Traffic")
    ts = api.transmit_state()
    ts.state = ts.START
    api.set_transmit_state(ts)

    time.sleep(11)
    wait_for(
        fn=lambda: flow_metrics_ok(api), fn_name="wait_for_flow_metrics"
    )

    ts = api.transmit_state()
    ts.state = ts.STOP
    api.set_transmit_state(ts)

    get_flow_metrics(api, True)


def flow_metrics_ok(api):
    for m in get_flow_metrics(api, False):
        if (
            m.transmit != m.STOPPED
            or m.frames_tx != 1000
            or m.frames_rx != 1000
        ):
            return False
    return True


def arp_ok(api):
    v4_gateway_macs_resolved = False

    get_config = api.get_config()
    v4_addresses = []

    for device in get_config.devices:
        for ethernet in device.ethernets:
            for v4_address in ethernet.ipv4_addresses:
                v4_addresses.append(v4_address.address)

    request = api.states_request()
    request.choice = request.IPV4_NEIGHBORS
    states = api.get_states(request)

    if len(v4_addresses) > 0:
        v4_link_layer_address = [
            state.link_layer_address
            for state in states.ipv4_neighbors
            if state.link_layer_address is not None
        ]
        if len(v4_addresses) == len(v4_link_layer_address):
            v4_gateway_macs_resolved = True
    else:
        v4_gateway_macs_resolved = True

    if v4_gateway_macs_resolved:
        return True

    return False


def wait_for(
    fn, fn_name="wait_for", interval_seconds=1, timeout_seconds=20
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


def get_flow_metrics(api, is_print):
    start = datetime.datetime.now()
    try:
        log.info("Getting flow metrics ...")
        req = api.metrics_request()
        req.flow.flow_names = []

        metrics = api.get_metrics(req).flow_metrics

        tb = table.Table(
            "Flow Metrics",
            [
                "Name",
                "Frames Tx",
                "Frames Rx",
                "FPS Tx",
                "FPS Rx",
                "Bytes Rx",
            ],
        )

        for m in metrics:
            tb.append_row(
                [
                    m.name,
                    m.frames_tx,
                    m.frames_rx,
                    m.frames_tx_rate,
                    m.frames_rx_rate,
                    m.bytes_rx,
                ]
            )
        if is_print:
            log.info(tb)
        return metrics
    finally:
        timer("get_flow_metrics", start)


if __name__ == "__main__":
    pytest.main(["-s", __file__])