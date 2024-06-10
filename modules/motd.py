from modules.common.module import BotModule
from mcstatus import JavaServer

class MatrixModule(BotModule):
    def __init__(self, name):
        super().__init__(name)
        self.host = None
        self.port = 25565
        
    def set_settings(self, data):
        super().set_settings(data)
        if data.get('host'):
            self.host = data['host']
        if data.get('port'):
            self.port = data['port']
            
    def get_settings(self):
        data = super().get_settings()
        data['host'] = self.host
        data['port'] = self.port
        return data

    async def matrix_message(self, bot, room, event):
        args = event.body.split()

        if len(args) > 1 and args[1] in ['set', 'setserver']:
            bot.must_be_owner(event)
            self.logger.info(f"room: {room.name} sender: {event.sender} is setting the server settings")
            if len(args) < 3:
                self.host = None
                return await bot.send_text(room, f'Usage: !{args[0]} {args[1]} [host] ([port])')
            self.host = args[2]
            if len(args) > 3:
                self.port = int(args[3])
            if not self.port:
                self.port = 25565
            bot.save_settings()
            return await bot.send_text(room, f'Set server settings: host: {self.host} port: {self.port}')

        self.logger.info(f"room: {room.name} sender: {event.sender} wants motd info")
        if not self.host:
            return await bot.send_text(room, f'No minecraft host info set!')


        server = JavaServer.lookup(f'{self.host}:{self.port}')
        status = server.status()
        if status:
            latency = round(server.ping(),0)
            if status.players.online > 0 :
                await bot.send_text(room, f'{self.host}:{self.port} (ping: {latency}ms) {status.players.online} player:')
                query = server.query()
                if query:
                    await bot.send_text(room, f"{', '.join(query.players.names)}")
            else:
                await bot.send_text(room, f'{self.host}:{self.port} (ping: {latency}ms) {status.players.online} player')
        else:
            await bot.send_text(room, f'Could not get minecraft server info.')

    def help(self):
        return 'Show info about a minecraft server'
    
    def long_help(self):
        text = self.help() + (
                '\n- "!motd": Get the status of the configured minecraft server')

        if bot and event and bot.is_owner(event):
            text += (
                    '\nOwner commands:'
                    '\n- "!motd set [host] ([port])": Set use the following host and port'
                    '\n- If no port is given, defaults to 25565')
        return text




