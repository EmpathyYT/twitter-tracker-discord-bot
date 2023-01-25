from datetime import datetime
import discord
from discord.ext import commands, tasks
import json
from components.processSharding import ShardedHandler
import dateutil.parser
from discord.utils import format_dt


with open("./components/config.json") as f:
    config = json.load(f)


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        self.handler = ShardedHandler(
            consumer_key=config['users'][0]['twitter_api_key'],
            consumer_secret=config['users'][0]['twitter_api_secret'],
            access_token=config['users'][0]['twitter_access_token'],
            access_token_secret=config['users'][0]['twitter_access_token_secret'],
            return_type=dict,
            wait_on_rate_limit=False
        )
    @tasks.loop(minutes=5)
    async def taska(self):
        print(f'{datetime.utcnow().strftime("%d/%m/%Y, %H:%M:%S")}: still alive.')
    
    @tasks.loop(minutes=16)  # to avoid ratelimit issues
    async def task(self):
        print('triggered')
        try:
            difference = await self.handler.run_shards()
            for user, followingDiff in difference.items():
                if followingDiff:
                    for following in followingDiff:
                        embed = discord.Embed(
                            color=discord.Colour.from_rgb(29, 161, 242),
                            title=f"{(await self.handler.get_user(id=user, user_auth=True))['data']['username']} followed {following['username']}!"
                        )
                        embed.add_field(
                            name="Follower Count:",
                            value=following['public_metrics']['followers_count'])
                        embed.add_field(
                            name="Account Created at:",
                            value=discord.utils.format_dt(dateutil.parser.isoparse(following['created_at'])))
                        # embed.add_field(
                        # name="Last tweet",
                        # value=self.handler.api.user_timeline(id=user, count=1)[0].entities.urls.url)
                        embed.add_field(name="Profile URL:", value=f"[Link](https://twitter.com/{(await self.handler.get_user(id=user, user_auth=True))['data']['username']})")
                        embed.set_thumbnail(url=following['profile_image_url'])
                        channel = self.get_channel(config['discord_channel_id'])
                        await channel.send(embed=embed)
        except Exception as e:
            print(e)
            

    @task.error
    async def error_handler(self, exception):
        print(str(exception))

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.utcnow()

        print(f'Ready: {self.user} (ID: {self.user.id})')
    
    async def setup_hook(self) -> None:
        await self.handler.create_shards(
            config['twitter_account_ids'], config['users'])
    
    async def on_ready(self):
        self.task.start()
        self.taska.start()
