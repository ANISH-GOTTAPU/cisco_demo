```python3 -m pytest demo/test_restpy.py --host="localhost:5050" --p1="10.39.64.137;2;1"  --p2="10.39.64.137;2;2" --log-cli-level=INFO```

```python3 -m pytest demo/test_snappi.py --host="localhost:40051" --p1="10.39.64.137;2;3"  --p2="10.39.64.137;2;4" --log-cli-level=INFO```

```go test -v -run TestGoSnappi -host "localhost:40051" -port1 "10.39.64.137;2;1" -port2 "10.39.64.137;2;2"```

```docker run --privileged --tty --detach -p 0.0.0.0:5050:443 --cap-add=SYS_ADMIN --cap-add=NET_ADMIN -i -d -v /sys/fs/cgroup:/sys/fs/cgroup --tmpfs /run ixnetworkweb_9.30.2212.22_image```


```docker compose -f docker-compose-v2.yml --profile all down```

```docker compose -f docker-compose-v2.yml --profile all up -d```