#!/bin/bash

openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/C=RU/ST=Saint-Petersburg/L=Saint-Petersburg/O=ITMO/OU=Security/CN=localhost"
