import argparse
import discord
import json

from url_substitute_bot import UrlSubstituteBot

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
    client = UrlSubstituteBot(url_replacements = config['url_replacements'],
                              webhook_url      = config['discord_webhook_url'],
                              bot_token        = config['discord_token'],
                              config_path      = args.config_file.name,
                              intents          = intents)
    client.run()


if __name__ == "__main__":
    exit(main())