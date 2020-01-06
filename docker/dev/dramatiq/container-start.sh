#!/bin/sh
cd /code && \
env PYTHONPATH=. dramatiq dramatiq_conf
