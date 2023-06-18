
 puts "      CBR0-UDP n0"
    puts "                \\"
    puts "                 n2 ---- n3"
    puts "                /"
    puts "      CBR1-TCP n1 "
    puts ""



set trailer .out

set tracefile sor$trailer
set cwfile cw$trailer
set rttfile rtt$trailer


# Creating the simulator object
set ns [new Simulator]

#file to store results
set nf [open $tracefile  w]
$ns trace-all $nf

set nff [open $cwfile  w]
set nrtt [open $rttfile  w]

#Finishing procedure
proc finish {} {
        global ns nf nff tracefile cwfile trailer nrtt
        $ns flush-trace
	# Process "sor.tr" to get sent packets
	exec awk {{ if ($1=="-" && $3==1 && $4=2) print $2, 49}}  $tracefile > tx$trailer
	# Process "sor.tr" to get dropped packets
	exec awk {{ if ($1=="d" && $3==2 && $4=3) print $2, 44}}  $tracefile  > drop$trailer
	exec awk {{  print $2,$3}}  $tracefile  > out$trailer

        close $nf
        close $nff
        close $nrtt
        exit 0
}
# TCP times recording procedure
proc record { } {
	global ns tcp1 nff nrtt
	# Getting the congestion window
    set cw  [$tcp1 set cwnd_]
    set tmp1 [expr 4 * [$tcp1 set rttvar_]]
   set rto [expr [$tcp1 set srtt_] + $tmp1]
        set rto [expr [$tcp1 set backoff_] * [$tcp1 set tcpTick_] * $rto ]

        set rttvar [$tcp1 set rttvar_]
        set rtt [$tcp1 set srtt_]
        set tcpTick [$tcp1 set tcpTick_]


	set now [$ns now]
	puts $nff "$now $cw"
	#puts $nrtt "$now $rto"
        puts $nrtt "$now $rtt $rttvar $tcpTick"
	$ns at [expr $now+0.1] "record"
}
#Create 4 nodes
#
#  n0
#  \
#   \
#    n2--------n3
#   /
#  /
# n1
 
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]

#Duplex lines between nodes
$ns duplex-link $n0 $n2 0.25Mb 20ms DropTail
$ns duplex-link $n1 $n2 0.25Mb 20ms DropTail
$ns duplex-link $n2 $n3 0.05Mb 0.5s DropTail
$ns queue-limit $n2 $n3 20


# Node 0:  UDP agent with Exponential  traffic generator
set udp0 [new Agent/UDP]
$ns attach-agent $n0 $udp0
set cbr0 [new Application/Traffic/Exponential]
$cbr0 set rate_ 0.05Mbps
$cbr0 attach-agent $udp0
$udp0 set class_ 0

set null0 [new Agent/Null]
$ns attach-agent $n3 $null0



$ns connect $udp0 $null0
$ns at 20.0 "$cbr0 start"
$ns at 180.0 "$cbr0 stop"

# Modify congention control procedures (slow start and linial increasing)
# Modify CWMAX (window_)
set tcp1 [new Agent/TCP/Newreno]
set cbr1 [new Application/Traffic/CBR]
$cbr1 set rate_ 0.05Mbps
$cbr1 attach-agent $tcp1
$tcp1 set window_ 10
$tcp1 set class_ 1



$ns attach-agent $n1 $tcp1
$tcp1 set tcpTick_ 0.01

set null1 [new Agent/TCPSink]
$ns attach-agent $n3 $null1


# Add a  CBR  traffic generator
set cbr1 [new Application/Traffic/CBR]
$cbr1 set rate_ 0.5Mbps
$cbr1 attach-agent $tcp1
$ns at 0.0 "$cbr1 start"
$ns at 0.0 "record"

$ns connect $tcp1 $null1 

# Stop simulation at  200 s.
$ns at 200.0 "finish"


#Run simulation
$ns run
