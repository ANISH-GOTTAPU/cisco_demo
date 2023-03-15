```go test -v -run TestQuickstart```

```python3 -m pytest demo/test_snappi.py --host="localhost:40051" --p1="10.36.75.242;2;15"  --p2="10.36.75.242;2;16" --log-cli-level=DEBUG```


```docker run --privileged --tty --detach -p 0.0.0.0:5050:443 --cap-add=SYS_ADMIN --cap-add=NET_ADMIN -i -d -v /sys/fs/cgroup:/sys/fs/cgroup --tmpfs /run ixnetworkweb_9.30.2212.22_image```