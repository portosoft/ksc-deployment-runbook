#!/bin/bash
export FEATURE_MESSAGE_BROKER_TYPE=nats
export NATS_ADDRESS=127.0.0.1
export NATS_PORT=4222
export NSQ_HOST=127.0.0.1
export NSQ_PORT=4222

cd /var/opt/kaspersky/ksc-web-console
./node pm.js pm.config.js
