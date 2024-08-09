#!/bin/sh

# Shell script to start proxy service

set -e # Exit on error

# Replace environment variables in the Nginx config file with their values
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf

 # Start Nginx in the foreground
nginx -g 'daemon off;'