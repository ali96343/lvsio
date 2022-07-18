
openssl \
 req -x509 \
 -newkey rsa:4096 \
 -keyout server.pem \
 -out server.pem \
 -days 365 \
 -nodes \
 -subj "/C=RU/ST=Saint Petersburg/O=SPB/OU=AliBsk/CN=localhost/emailAddress=ab96343@gmail.com"

