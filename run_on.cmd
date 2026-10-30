server python3 server.py > server_on.out 2>&1 < /dev/null &
server iperf -s -u > iperf_server_on.out 2>&1 < /dev/null &
sh sleep 2
p3 iperf -u -c 10.0.0.1 -b 15M -t 30 > iperf_on.out 2>&1 < /dev/null &
p1 python3 client.py 1 > p1_on.out 2>&1 < /dev/null &
p2 python3 client.py 2 > p2_on.out 2>&1 < /dev/null &
sh sleep 35
sh tail -6 server_on.out
sh cat iperf_server_on.out
