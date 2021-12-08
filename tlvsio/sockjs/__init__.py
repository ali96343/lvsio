from py4web import action, request


# pls, run websockets server - look at utils/wsservers.py.txt
# test example for sockjs 
# tested with ./py4web.py  run -s  tornadoSioWsServer  apps

@action("sockjs/index")
@action.uses("sockjs/index.html")
def index():
    sockjs_url= 'http://127.0.0.1:8000/sockjs' 
    # sockjs_url="""'http://' + window.location.host + '/sockjs'"""
    return dict(sockjs_url=sockjs_url)


