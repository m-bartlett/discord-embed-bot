import discord
import json
import re
import aiohttp


class UrlSubstituteBot(discord.Client):
    _url_regex = re.compile(r"https?:\/\/[^\/]+\/")

    def __init__(self, *,
                 url_replacements: dict[str, str],
                 webhook_url:      str,
                 bot_token:        str,
                 config_path:      str = 'config.json',
                 intents:          discord.Intents,
                 owner_id:         int = 0,
                 **kwargs:         any):
        super().__init__(intents=intents, **kwargs)
        self.url_replacements = url_replacements
        self._token = bot_token
        self.config_path = config_path
        self.owner_id = owner_id
        self.webhook = discord.Webhook.from_url(webhook_url, bot_token=bot_token, session=None)
        self.text_command_to_handler_map: dict[str, callable] = {
            "help": self._text_command_help,
            "domains": self._text_command_domains,
            "update": self._text_command_update,
            "owner": self._text_command_check_owner,
        }


    def _url_sub_repl(self, url_match: re.Match):
        url = url_match[0]
        protocol, _, domain, *rest = url.split('/')
        if (new_domain := self.url_replacements.get(domain)) is not None:
            new_rest = '/'.join(rest)
            new_url = f"{protocol}//{new_domain}/{new_rest}"
            return new_url
        return url


    def _url_sub(self, body: str):
        return self._url_regex.sub(self._url_sub_repl, body)


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

        new_content = self._url_sub(message.content)
        if new_content != message.content:
            await message.delete()
            async with aiohttp.ClientSession() as session:
                self.webhook.session = session
                username = message.author.nick or message.author.global_name
                await self.webhook.edit(channel=message.channel)
                await self.webhook.send(new_content,
                                        username=f"{username} (URL substituted)",
                                        avatar_url=message.author.display_avatar.url)


    async def handle_text_command(self, message: discord.Message):
        body = message.clean_content
        begin, _, end = body.partition(f"@{self.user.name}")
        tokens = [t for t in (begin+end).strip().split(' ') if len(t)>0]
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


    @staticmethod
    def _format_error(body: str):
        return ("```ansi\n"
                f"[31m{body}[0m\n"
                "```")


    async def _send_error(self, message: discord.Message, body: str):
        body_formatted = self._format_error(body)
        await message.channel.send(content=body_formatted)


    async def _is_user_privileged(self, message: discord.Message):
        if message.author.id == self.owner_id:
            return True
        else:
            await self._send_error(message, "Permission denied: you are not a privileged user.")
            return False


    async def _text_command_check_owner(self, message: discord.Message, tokens: list[str]):
        if await self._is_user_privileged(message):
            await message.channel.send(content="You are the bot owner")
        else:
            return


    async def _text_command_update(self, message: discord.Message, tokens: list[str]):
        if not await self._is_user_privileged(message):
            return
        args = tokens[1:]
        if len(args) < 2:
            await self._send_error(message, "Usage: update <source_domain> <domain_substitute>")
            return
        source_domain = args[0]
        domain_substitute = args[1]
        if self.url_replacements.get(source_domain) is None:
            response = (f"Given source domain {source_domain} is not currently configured.\n"
                        f"Configured domains are: {', '.join(self.url_replacements.keys())}")
            await self._send_error(message, response)
            return
        self.url_replacements[source_domain] = domain_substitute
        self.write_config()
        response = (f"{source_domain} will now get substituted with {domain_substitute}.")
        await message.channel.send(content=response)
        return True


    def write_config(self):
        config = { "url_replacements":    self.url_replacements,
                   "discord_token":       self._token,
                   "discord_webhook_url": self.webhook.url,
                   "owner_id":            self.owner_id }
        with open(self.config_path, 'w') as config_fp:
            json.dump(config, config_fp, indent=4, sort_keys=True)
        print(f"Updated config @ {self.config_path} with: "
              f"{json.dumps(config, indent=4, sort_keys=True)}")