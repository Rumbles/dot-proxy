FROM ubuntu:latest
LABEL DNS over TLS container

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y python3 python3-getdns python3-dnslib supervisor

COPY udp-dot-proxy.py /usr/bin/udp-dot-proxy
COPY udp-dot-proxy.conf /etc/supervisor/conf.d/udp-dot-proxy.conf
COPY tcp-dot-proxy.py /usr/bin/tcp-dot-proxy
COPY tcp-dot-proxy.conf /etc/supervisor/conf.d/tcp-dot-proxy.conf

RUN chmod 755 /usr/bin/udp-dot-proxy
RUN chmod 755 /usr/bin/tcp-dot-proxy

EXPOSE 53 53/udp

CMD ["/usr/bin/supervisord", "-n"]
