import json
import discord

from components.bot import Bot
from components.processSharding import ShardedHandler

with open("./components/config.json") as f:
    config = json.load(f)

bot = Bot(command_prefix='.', intents=discord.Intents.default())


bot.run(config['discord_token'])
    