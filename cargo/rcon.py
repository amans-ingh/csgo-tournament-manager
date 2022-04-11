import aiorcon
import asyncio
import json
from cargo import application


class GameServer:
    def __init__(self, ip, port, password, match_id):
        self.ip = ip
        self.password = password
        self.match_id = match_id
        self.port = port

    def load_match(self):
        async def main(loop, command):
            rcon = await aiorcon.RCON.create(self.ip, self.port, self.password, loop)
            output = await(rcon(command))
            rcon.close()
            return output

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(main(loop, 'get5_loadmatch_url "' + application.config['SERVER_URL'] +
                                            '/api/match/' + str(self.match_id) + '/config"'))

    def server_status(self):
        async def main(loop, command):
            rcon = await aiorcon.RCON.create(self.ip, self.port, self.password, loop)
            output = await(rcon(command))
            rcon.close()
            return output

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        output = loop.run_until_complete(main(loop, 'get5_status'))
        i = output.index('L', 0)
        json_output = json.loads(output[0:i])
        return json_output
