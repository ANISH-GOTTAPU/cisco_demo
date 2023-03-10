// go:build all

package quicktest

import (
	"testing"
	"time"

	"github.com/open-traffic-generator/snappi/gosnappi"
)

const (
	plen4 = 30
	plen6 = 126
)

type Attributes struct {
	IPv4    string
	IPv6    string
	MAC     string
	Name    string // Interface name, only applied to ATE ports.
	Desc    string // Description, only applied to DUT interfaces.
	IPv4Len uint8  // Prefix length for IPv4.
	IPv6Len uint8  // Prefix length for IPv6.
	MTU     uint16
}

var (
	ateSrc = Attributes{
		Name:    "ateSrc",
		MAC:     "02:11:01:00:00:01",
		IPv4:    "192.0.2.1",
		IPv6:    "2001:db8::1",
		IPv4Len: plen4,
		IPv6Len: plen6,
	}

	ateDst = Attributes{
		Name:    "ateDst",
		MAC:     "02:12:01:00:00:01",
		IPv4:    "192.0.2.2",
		IPv6:    "2001:db8::2",
		IPv4Len: plen4,
		IPv6Len: plen6,
	}
)

func TestQuickstart(t *testing.T) {
	// Create a new API handle to make API calls against OTG
	api := gosnappi.NewApi()

	// Set the transport protocol to HTTP
	api.NewHttpTransport().SetLocation("https://localhost:8443").SetVerify(false)

	// api.NewGrpcTransport().SetLocation("localhost:40051").SetRequestTimeout(3600 * time.Second)

	// Create a new traffic configuration that will be set on OTG
	config := api.NewConfig()

	// Add a test port to the configuration
	srcPort := config.Ports().Add().SetName("port1").SetLocation("10.36.75.242;2;15")
	dstPort := config.Ports().Add().SetName("port2").SetLocation("10.36.75.242;2;16")

	srcDev := config.Devices().Add().SetName(ateSrc.Name)
	srcEth := srcDev.Ethernets().Add().SetName(ateSrc.Name + ".eth").SetMac(ateSrc.MAC)
	srcEth.Connection().SetChoice(gosnappi.EthernetConnectionChoice.PORT_NAME).SetPortName(srcPort.Name())
	srcEth.Ipv4Addresses().Add().SetName(ateSrc.Name + ".IPv4").SetAddress(ateSrc.IPv4).SetGateway(ateDst.IPv4).SetPrefix(int32(ateSrc.IPv4Len))

	dstDev := config.Devices().Add().SetName(ateDst.Name)
	dstEth := dstDev.Ethernets().Add().SetName(ateDst.Name + ".eth").SetMac(ateDst.MAC)
	dstEth.Connection().SetChoice(gosnappi.EthernetConnectionChoice.PORT_NAME).SetPortName(dstPort.Name())
	dstEth.Ipv4Addresses().Add().SetName(ateDst.Name + ".IPv4").SetAddress(ateDst.IPv4).SetGateway(ateSrc.IPv4).SetPrefix(int32(ateDst.IPv4Len))

	// Configure a flow and set previously created test port as one of endpoints
	flow := config.Flows().Add().SetName("f1")
	flow.TxRx().Device().
		SetTxNames([]string{ateSrc.Name + ".IPv4"}).
		SetRxNames([]string{ateDst.Name + ".IPv4"})
	// and enable tracking flow metrics
	flow.Metrics().SetEnable(true)

	// Configure number of packets to transmit for previously configured flow
	flow.Duration().FixedPackets().SetPackets(100)
	// and fixed byte size of all packets in the flow
	flow.Size().SetFixed(128)

	// Configure protocol headers for all packets in the flow
	pkt := flow.Packet()
	eth := pkt.Add().Ethernet()
	ipv4 := pkt.Add().Ipv4()

	eth.Dst().SetValue(ateDst.MAC)
	eth.Src().SetValue(ateSrc.MAC)

	ipv4.Src().SetValue(ateSrc.IPv4)
	ipv4.Dst().SetValue(ateDst.IPv4)

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

	time.Sleep(180 * time.Second)
	api.SetProtocolState(api.NewProtocolState().SetState(gosnappi.ProtocolStateState.START))

	time.Sleep(180 * time.Second)
	// Start transmitting the packets from configured flow
	ts := api.NewTransmitState()
	ts.SetState(gosnappi.TransmitStateState.START)
	if _, err := api.SetTransmitState(ts); err != nil {
		t.Fatal(err)
	}

	// Fetch metrics for configured flow
	req := api.NewMetricsRequest()
	req.Flow().SetFlowNames([]string{flow.Name()})
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
		time.Sleep(100 * time.Millisecond)
	}
}
