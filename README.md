# discord-embed-bot

A passive Discord bot which substitutes messaged URLs of common social media sites with rich-embed equivalents

## Setup

### Create a `config.json` or similar file
Run `cp config.json.example config.json` to start with the configuration template.

> [!IMPORTANT]
> You **must** change the values for `discord_token` and `discord_webhook_url` to that of your bot and your target server's webhook. Currently the this bot code only supports occupying one server at a time, and it will likely fail in unexpected ways if added to multiple servers. The below steps will instruct how to acquire the values needed for these configuration options.

### Discord Application (Bot) Config:

Create a bot and copy its bot token. Paste the token into the value string for the `discord_token` key in your `config.json` file.

<https://ptb.discord.com/developers/applications>

<https://discord.com/developers/docs/intro>

Scopes:
  * applications.commands
  * bot

Permissions:
  * Embed Links
  * Manage Messages
  * Manage Webhooks
  * Send Messages
  * View Channels

### Invite to Discord Server
From the developer port, generate an invite link and navigate to it. You may need to authenticate to your discord account during the OAuth process, but you will be given a consent screen to confirm adding the bot to your server. Accept and manage the bot's channel access accordingly, it will monitor all channels it is given access to.

### Create a Webhook for the Bot
The bot makes use of a dedicated webhook to simulate impersonating users when substituting URLs. The bot needs permission to "manange" this webhook, as webhooks can only target one channel on the server at any given time. The bot changes which channel the webhook targets when it identifies a message with a configured URL to substitute to be able to post to that channel. As of the latest version, the bot will not create any webhooks and the user will need to create and specify the webhook URL in the `config.json`

### Install dependencies
```console
$ pip install -r requirements.txt
```

## Running
If you created the `config.json` in the root of this repository, simply run `python main.py`. Otherwise, use the `--config` or `-c` flag to specify any alternative path to the configuration file you created, e.g. `python main.py -c /path/to/config.json`



## Development

### Run Tests
```sh
pip install -r requirements-dev.txt
pytest
```