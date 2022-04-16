import aiorcon
import asyncio
import json
from cargo import application


async def main(loop, command, ip, port, password):
    try:
        rcon = await asyncio.wait_for(aiorcon.RCON.create(ip, port, password, loop), timeout=2.0)
        output = await(rcon(command))
        rcon.close()
    except:
        output = False
    return output


class GameServer:
    def __init__(self, ip, port, password):
        self.ip = ip
        self.password = password
        self.port = port

    def load_match(self, tour_id, round_num, match_num):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(main(loop, 'get5_loadmatch_url "' +
                                            application.config['SERVER_URL'] +
                                            '/api/tour/' + str(tour_id) +
                                            '/round/' + str(round_num) +
                                            '/match/' + str(match_num) +
                                            '/config"',
                                            self.ip,
                                            self.port,
                                            self.password))

    def end_match(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(main(loop, 'get5_endmatch',
                                            self.ip,
                                            self.port,
                                            self.password))

    def server_status(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        output = loop.run_until_complete(main(loop, 'get5_status', self.ip, self.port, self.password))
        if output:
            try:
                if 'L' in output:
                    i = output.index('L', 0)
                    json_output = json.loads(output[0:i])
                else:
                    json_output = json.loads(output)
                return json_output
            except:
                return False
        return False

    def check_plugins(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        output = loop.run_until_complete(main(loop, 'sm plugins list', self.ip, self.port, self.password))
        if not output:
            return False
        result = {"get5": False, "api": False}
        if '"Get5"' in str(output):
            result["get5"] = True
            result["api"] = False
            if '"Get5 Web API Integration"' in str(output):
                result["api"] = True
        return result

    def server_ip(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        output = loop.run_until_complete(main(loop, 'status', self.ip, self.port, self.password))
        if output:
            data = output.split('\n')
            ip_add = data[2].split(' ')[-1].split(')')[0]
            return ip_add
        return False
