#!/bin/bash

docker stop dot-proxy

docker build -t dot-proxy .

docker run -d --rm	--net=bridge --name dot-proxy dot-proxy
