curl --include \
       --no-buffer \
       --header "Connection: Upgrade" \
       --header "Upgrade: websocket" \
       --header "Host: 127.0.0.1" \
       --header "Origin: http://127.0.0.1:8000" \
       --header "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
       --header "Sec-WebSocket-Version: 13" \
       http://127.0.0.1:8000/
