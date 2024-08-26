import discord
import json
import re
import argparse
import aiohttp


class EmbedFriendlyUrlSubstitutorBot(discord.Client):
    _url_regex = re.compile(r"https?:\/\/[^\s]+")

    def __init__(self,
                 *,
                 url_replacements: dict[str, str],
                 webhook_url:      str,
                 bot_token:        str,
                 config_path:      str = 'config.json',
                 intents:          discord.Intents,
                 **kwargs:         any):
        super().__init__(intents=intents, **kwargs)
        self.url_replacements = url_replacements
        self._token = bot_token
        self.config_path = config_path
        self.webhook = discord.Webhook.from_url(webhook_url, bot_token=bot_token, session=None)
        self.text_command_to_handler_map: dict[str, callable] = {
            "help": self._text_command_help,
            "domains": self._text_command_domains,
        }


    def _url_replace(self, url_match: re.Match):
        url = url_match[0]
        protocol, _, domain, *rest = url.split('/')
        if (new_demain := self.url_replacements.get(domain)) is not None:
            new_rest = '/'.join(rest)
            new_rest = f"/{new_rest}" if new_rest else ''
            new_url = f"{protocol}//{new_demain}{new_rest}"
            return new_url
        else:
            return url


    async def on_ready(self):
        print(f'Logged on as {self.user}!')


    def run(self):
        return super().run(self._token)


    async def on_message(self, message: discord.Message):

        if message.author.id == self.user.id:
            return
        elif message.webhook_id:
            return
        elif self.user.mentioned_in(message):
            return await self.handle_text_command(message)

        new_content, substitutions_made = self._url_regex.subn(self._url_replace, message.content)
        if substitutions_made > 0:
            await message.delete()
            async with aiohttp.ClientSession() as session:
                self.webhook.session = session
                await self.webhook.edit(channel=message.channel)
                await self.webhook.send(new_content,
                                        username=f"{message.author.nick} (URL substituted)",
                                        avatar_url=message.author.display_avatar.url)


    async def handle_text_command(self, message: discord.Message):
        body = message.clean_content
        begin, _, end = body.partition(f"@{self.user.name}")
        tokens = (begin+end).strip().split(' ')
        try:
            if handler := self.text_command_to_handler_map.get(tokens[0]):
                await handler(message, tokens)
        except IndexError:
            return


    async def _text_command_domains(self, message: discord.Message, tokens: list[str]):
        body = f"```json\n{json.dumps(self.url_replacements, indent=4)}\n```"
        await message.channel.send(content=body)


    async def _text_command_help(self, message: discord.Message, tokens: list[str]):
        body = '\n'.join(f"* `{command}`" for command in self.text_command_to_handler_map.keys())
        await message.channel.send(content=body)


    def write_config(self):
        config = { "url_replacements": self.url_replacements,
                   "discord_token": self._token,
                   "discord_webhook_url": self.webhook.url }
        with open(self.config_path, 'w') as config_fp:
            json.dump(config, config_fp, indent=4, sort_keys=True)




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c',
                        dest='config_file',
                        default='config.json',
                        type=argparse.FileType('rb'),
                        help="Config file path to load")
    args = parser.parse_args()
    config = json.load(args.config_file)
    intents = discord.Intents.default()
    intents.message_content = True
    client = EmbedFriendlyUrlSubstitutorBot(url_replacements = config['url_replacements'],
                                            webhook_url      = config['discord_webhook_url'],
                                            bot_token        = config['discord_token'],
                                            config_path      = args.config_file.name,
                                            intents          = intents)
    client.run()


if __name__ == "__main__":
    exit(main())