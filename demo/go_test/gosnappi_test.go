// go:build all

package gosnappitest

import (
	"flag"
	"testing"
	"time"

	"github.com/cisco_demo/table"
	"github.com/open-traffic-generator/snappi/gosnappi"
)

type Attributes struct {
	IPv4        string
	IPv6        string
	MAC         string
	Name        string // Interface name, only applied to ATE ports.
	Desc        string // Description, only applied to DUT interfaces.
	IPv4_routes string // Prefix length for IPv4.
	IPv6_routes string // Prefix length for IPv6.
	MTU         uint16
}

var (
	txBgpd = Attributes{
		Name:        "tx_bgpd",
		MAC:         "00:10:94:00:01:91",
		IPv4:        "166.1.1.2",
		IPv4_routes: "10.1.1.1",
		IPv6_routes: "10:1:1:1:1:1:1:1",
	}

	txIsisd = Attributes{
		Name:        "tx_isisd",
		MAC:         "00:10:94:00:01:AB",
		IPv4:        "170.1.1.2",
		IPv6:        "170:1:1::2",
		IPv4_routes: "30.1.1.1",
	}

	rxBgpd = Attributes{
		Name:        "rx_bgpd",
		MAC:         "00:10:94:00:01:AC",
		IPv4:        "166.1.1.1",
		IPv4_routes: "20.1.1.1",
		IPv6_routes: "20:1:1:1:1:1:1:1",
	}

	rxIsisd = Attributes{
		Name:        "rx_isisd",
		MAC:         "00:10:94:00:01:AD",
		IPv4:        "170.1.1.1",
		IPv6:        "170:1:1::1",
		IPv4_routes: "40.1.1.1",
	}
)

var host = flag.String("host", "localhost:40051", "description of the host flag")
var port1 = flag.String("port1", "10.36.75.242;2;13", "description of the p1 flag")
var port2 = flag.String("port2", "10.36.75.242;2;14", "description of the p2 flag")

func TestGoSnappi(t *testing.T) {

	// Create a new API handle to make API calls against OTG
	api := gosnappi.NewApi()
	// Set the transport protocol to HTTP
	// api.NewHttpTransport().SetLocation("https://localhost:8443").SetVerify(false)

	api.NewGrpcTransport().SetLocation(*host).SetRequestTimeout(3600 * time.Second)

	// Create a new traffic configuration that will be set on OTG
	config := api.NewConfig()

	// Add a test port to the configuration
	p1 := config.Ports().Add().SetName("p1").SetLocation(*port1)
	p2 := config.Ports().Add().SetName("p2").SetLocation(*port2)

	txd1 := config.Devices().Add().SetName(txBgpd.Name)
	txd2 := config.Devices().Add().SetName(txIsisd.Name)
	rxd1 := config.Devices().Add().SetName(rxBgpd.Name)
	rxd2 := config.Devices().Add().SetName(rxIsisd.Name)

	// Configure tx_bgpd BGP
	txBgpdEth := txd1.Ethernets().
		Add().
		SetName(txBgpd.Name + "eth").
		SetMac(txBgpd.MAC).
		SetMtu(1500)

	txBgpdEth.Connection().SetPortName(p1.Name())

	txBgpdIp := txBgpdEth.
		Ipv4Addresses().
		Add().
		SetName(txBgpd.Name + "ip").
		SetAddress(txBgpd.IPv4).
		SetGateway(rxBgpd.IPv4).
		SetPrefix(24)

	txBgp := txd1.Bgp().
		SetRouterId(txBgpd.IPv4)

	txBgpv4 := txBgp.
		Ipv4Interfaces().Add().
		SetIpv4Name(txBgpdIp.Name())

	txBgpv4Peer := txBgpv4.
		Peers().
		Add().
		SetAsNumber(6000).
		SetAsType(gosnappi.BgpV4PeerAsType.EBGP).
		SetPeerAddress(rxBgpd.IPv4).
		SetName("dtxBgpv4Peer")

	txBgpv4Peer.LearnedInformationFilter().SetUnicastIpv4Prefix(true).SetUnicastIpv6Prefix(true)

	txBgpv4PeerRrV4 := txBgpv4Peer.
		V4Routes().
		Add().
		SetName("txBgpv4PeerRrV4")

	txBgpv4PeerRrV4.Addresses().Add().
		SetAddress(txBgpd.IPv4_routes).
		SetPrefix(32).
		SetCount(500).
		SetStep(1)

	// Configure rx_bgpd BGP
	rxBgpdEth := rxd1.Ethernets().
		Add().
		SetName(rxBgpd.Name + "eth").
		SetPortName(p2.Name()).
		SetMac(rxBgpd.MAC).
		SetMtu(1500)

	rxBgpdIp := rxBgpdEth.
		Ipv4Addresses().
		Add().
		SetName(rxBgpd.Name + "ip").
		SetAddress(rxBgpd.IPv4).
		SetGateway(txBgpd.IPv4).
		SetPrefix(24)

	rxBgp := rxd1.Bgp().
		SetRouterId(rxBgpd.IPv4)

	rxBgpv4 := rxBgp.
		Ipv4Interfaces().Add().
		SetIpv4Name(rxBgpdIp.Name())

	rxBgpv4Peer := rxBgpv4.
		Peers().
		Add().
		SetAsNumber(6500).
		SetAsType(gosnappi.BgpV4PeerAsType.EBGP).
		SetPeerAddress(txBgpd.IPv4).
		SetName("rxBgpv4Peer")

	rxBgpv4Peer.LearnedInformationFilter().SetUnicastIpv4Prefix(true).SetUnicastIpv6Prefix(true)

	rxBgpv4PeerRrV4 := rxBgpv4Peer.
		V4Routes().
		Add().
		SetName("rxBgpv4PeerRrV4")

	rxBgpv4PeerRrV4.Addresses().Add().
		SetAddress(rxBgpd.IPv4_routes).
		SetPrefix(32).
		SetCount(500).
		SetStep(1)

	// Configure tx_isis
	txIsisdEth := txd2.Ethernets().
		Add().
		SetName(txIsisd.Name + "eth").
		SetPortName(p1.Name()).
		SetMac(txIsisd.MAC).
		SetMtu(1500)

	txIsisdEth.Ipv4Addresses().
		Add().
		SetName(txIsisd.Name + "ip").
		SetAddress(txIsisd.IPv4).
		SetGateway(rxIsisd.IPv4).
		SetPrefix(24)

	txdIsis := txd2.Isis().SetSystemId("640000000000").SetName("txd2Isis")

	txdIsis.Interfaces().
		Add().
		SetEthName(txIsisdEth.Name()).
		SetNetworkType(gosnappi.IsisInterfaceNetworkType.BROADCAST).
		SetLevelType(gosnappi.IsisInterfaceLevelType.LEVEL_2).
		SetName("tdxIsisInt")

	txIsisRrV4 := txdIsis.
		V4Routes().
		Add().SetName("txIsisRrV4").SetLinkMetric(10)

	txIsisRrV4.Addresses().Add().
		SetAddress(txIsisd.IPv4_routes).
		SetPrefix(32).
		SetCount(500).
		SetStep(1)

	// Configure rx_isis
	rxIsisdEth := rxd2.Ethernets().
		Add().
		SetName(rxIsisd.Name + "eth").
		SetPortName(p2.Name()).
		SetMac(rxIsisd.MAC).
		SetMtu(1500)

	rxIsisdEth.Ipv4Addresses().
		Add().
		SetName(rxIsisd.Name + "ip").
		SetAddress(rxIsisd.IPv4).
		SetGateway(txIsisd.IPv4).
		SetPrefix(24)

	rxdIsis := rxd2.Isis().SetSystemId("640000000001").SetName("rxd2Isis")

	rxdIsis.Interfaces().
		Add().
		SetEthName(rxIsisdEth.Name()).
		SetNetworkType(gosnappi.IsisInterfaceNetworkType.BROADCAST).
		SetLevelType(gosnappi.IsisInterfaceLevelType.LEVEL_2).
		SetName("rdxIsisInt")

	rxIsisRrV4 := rxdIsis.
		V4Routes().
		Add().SetName("rxIsisRrV4").SetLinkMetric(10)

	rxIsisRrV4.Addresses().Add().
		SetAddress(rxIsisd.IPv4_routes).
		SetPrefix(32).
		SetCount(500).
		SetStep(1)

	// Configure a flow and set previously created test port as one of endpoints
	flow := config.Flows().Add().SetName("BGP")
	flow.TxRx().Device().
		SetTxNames([]string{txBgpv4PeerRrV4.Name()}).
		SetRxNames([]string{rxBgpv4PeerRrV4.Name()})
	// and enable tracking flow metrics
	flow.Metrics().SetEnable(true)

	// Configure number of packets to transmit for previously configured flow
	flow.Duration().FixedPackets().SetPackets(1000)
	// and fixed byte size of all packets in the flow
	flow.Size().SetFixed(128)

	// Configure protocol headers for all packets in the flow
	pkt := flow.Packet()
	eth := pkt.Add().Ethernet()
	ipv4 := pkt.Add().Ipv4()

	eth.Src().SetValue(txBgpd.MAC)

	ipv4.Src().SetValue(txBgpd.IPv4_routes)
	ipv4.Dst().SetValue(rxBgpd.IPv4_routes)

	flow2 := config.Flows().Add().SetName("ISIS")
	flow2.TxRx().Device().
		SetTxNames([]string{txIsisRrV4.Name()}).
		SetRxNames([]string{rxIsisRrV4.Name()})
	// and enable tracking flow metrics
	flow2.Metrics().SetEnable(true)

	// Configure number of packets to transmit for previously configured flow
	flow2.Duration().FixedPackets().SetPackets(1000)
	// and fixed byte size of all packets in the flow
	flow2.Size().SetFixed(128)

	// Configure protocol headers for all packets in the flow
	f2_pkt := flow2.Packet()
	f2_pkt_eth := f2_pkt.Add().Ethernet()
	f2_pkt_ipv4 := f2_pkt.Add().Ipv4()

	f2_pkt_eth.Src().SetValue(txIsisd.MAC)

	f2_pkt_ipv4.Src().SetValue(txIsisd.IPv4_routes)
	f2_pkt_ipv4.Dst().SetValue(rxIsisd.IPv4_routes)

	// Optionally, print JSON representation of config
	if j, err := config.ToJson(); err != nil {
		t.Fatal(err)
	} else {
		t.Log("Configuration: ", j)
	}

	// Push traffic configuration constructed so far to OTG
	if _, err := api.SetConfig(config); err != nil {
		t.Fatal(err)
	}

	time.Sleep(40 * time.Second)
	api.SetProtocolState(api.NewProtocolState().SetState(gosnappi.ProtocolStateState.START))

	time.Sleep(40 * time.Second)
	// Start transmitting the packets from configured flow
	ts := api.NewTransmitState()
	ts.SetState(gosnappi.TransmitStateState.START)
	if _, err := api.SetTransmitState(ts); err != nil {
		t.Fatal(err)
	}

	// Fetch metrics for configured flow
	req := api.NewMetricsRequest()
	req.Flow().SetFlowNames([]string{flow.Name(), flow2.Name()})
	// and keep polling until either expectation is met or deadline exceeds
	deadline := time.Now().Add(10 * time.Second)
	for {
		metrics, err := api.GetMetrics(req)
		if err != nil || time.Now().After(deadline) {
			t.Fatalf("err = %v || deadline exceeded", err)
		}
		// print YAML representation of flow metrics
		t.Log(metrics)
		if metrics.FlowMetrics().Items()[0].Transmit() == gosnappi.FlowMetricTransmit.STOPPED {
			break
		}

	}
	mr := api.NewMetricsRequest()
	mr.Flow()
	res, _ := api.GetMetrics(mr)

	tb := table.NewTable(
		"Flow Metrics",
		[]string{
			"Name",
			"State",
			"Frames Tx",
			"Frames Rx",
			"FPS Tx",
			"FPS Rx",
			"Bytes Tx",
			"Bytes Rx",
		},
		15,
	)
	for _, v := range res.FlowMetrics().Items() {
		if v != nil {
			tb.AppendRow([]interface{}{
				v.Name(),
				v.Transmit(),
				v.FramesTx(),
				v.FramesRx(),
				v.FramesTxRate(),
				v.FramesRxRate(),
				v.BytesTx(),
				v.BytesRx(),
			})
		}
	}

	t.Log(tb.String())
}
