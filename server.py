import os
import asyncio
import json
from aiohttp import web


async def handle(request):
    try:
        with open("templates/index.html", 'rb') as index:
            return web.Response(body=index.read())
    except FileNotFoundError:
        pass
    return web.Response(status=404)


async def wshandler(request):
    print("Connected")
    app = request.app
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    while True:
        msg = await ws.receive()
        if msg.tp == web.MsgType.text:
            print("Got message %s" % msg.data)

            data = msg.data

            if type(data) == str:
                p = await asyncio.create_subprocess_shell(data, stdout=asyncio.subprocess.PIPE)
                s = await p.stdout.readline()
                while s:
                    print(s)
                    ws.send_str(s.decode("utf-8"))
                    s = await p.stdout.readline()


        elif msg.tp == web.MsgType.close:
            break

    print("Closed connection")
    return ws



event_loop = asyncio.get_event_loop()
event_loop.set_debug(True)

app = web.Application()

app.router.add_route('GET', '/connect', wshandler)
app.router.add_route('GET', '/', handle)
app.router.add_static('/static', "static")

# get port for heroku
web.run_app(app, port=5555)
