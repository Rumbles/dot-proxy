# dot-proxy
A DNS over TLS proxy written in python

## N26 SRE Challenge

### DNS to DNS-over-TLS proxy
I was recently asked if I could write a DNS proxy, receiving TCP or UDP DNS traffic I was able to run sockets in a thread and listen to multiple requests and proxy them to Cloudflare's DNS over TLS offering.

I had to write 2 scripts, one for UDP and one for TCP, then run each as a supervisor process. This then runs inside a docker container

### Testing

run the docker script:

`./docker.sh`

Now you should have a running container listening on 53 and 53/udp, you can connect with:

`docker exec -it dot-proxy /bin/bash`

Then tail the logs with:

`tail -f /var/log/supervisor/*`

And test it by running (assuming the IP address is right):

`dig google.com -t A @172.17.0.2`
`dig google.com -t A @172.17.0.2 +tcp`

I also tested the threading works, I did this by running tcpdump:

`tcpdump -i docker0 -vvv -w docker.pcap`

I then opened a tmux session and made 4 requests at once (I did TCP first, then UDP), in the PCAP I could see each request being received and acknowledged (TCP), then the DNS over TLS requests run, then finally all of the responses go back to the requester. Since this all happens in ~0.15s for TCP and ~0.14s for UDP it would be difficult to confirm this is running in parallel otherwise.
