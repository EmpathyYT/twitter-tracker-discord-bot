import asyncio
from components.twitterHandler import TwitterHandler
import json
from components.errorHandler import TwitterHandlerException

with open('./components/config.json') as f:
    config = json.load(f)


class ShardedHandler(TwitterHandler):
    def __init__(self, bearer_token=None, consumer_key=None, consumer_secret=None, access_token=None,
                 access_token_secret=None, *, return_type=..., wait_on_rate_limit=False):
        super().__init__(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret,
                         return_type=return_type, wait_on_rate_limit=wait_on_rate_limit)
        self.sharded_handler: dict[TwitterHandler, list] = {}

    async def shard_list(self, users: list, keys: list) -> list:
        userdict = {}
        shardedlist = []
        usersinfo = await super().get_users(ids=users, user_auth=True,
                                            user_fields=["public_metrics"])
        usersinfo = usersinfo['data']
        for info in usersinfo:
            userdict.update(
                {info['id']: info['public_metrics']['following_count']})

        userdict = sorted(userdict.items(), key=lambda x: x[1])
        userdict = dict(userdict)
        i = 0
        listofusers = []
        for key, value in userdict.items():
            if (i + value) >= 15_000:

                shardedlist.append(listofusers)
                listofusers = []
                i = 0

            listofusers.append(key)
            i += value
            if key == list(userdict.keys())[(len(userdict.keys()) - 1)]:
                shardedlist.append(listofusers)

        if len(shardedlist) > len(keys):
            raise TwitterHandlerException(
                f"Not enough keys to run,\nKeys provided: {len(keys)}, keys required: {len(shardedlist)}")

        keyscountrem = len(keys) - len(shardedlist)
        if keyscountrem > 0:
            for i in range(1, keyscountrem + 1):
                subshardedlist = []
                maxlist = max(shardedlist, key=len)
                if (len(maxlist) > 1) and (len(maxlist) % 2 == 0):
                    subshardedlist.append(maxlist[:int(len(maxlist) / 2)])
                    subshardedlist.append(maxlist[int(len(maxlist) / 2):])

                elif (len(maxlist) > 1) and (len(maxlist) % 2 != 0):
                    splits = int((len(maxlist) + 1) / 2)
                    subshardedlist.append(maxlist[:splits])
                    subshardedlist.append(maxlist[splits:])

                else:
                    break

                if subshardedlist:
                    shardedlist.remove(maxlist)
                    shardedlist.extend(subshardedlist)

        return shardedlist

    async def shard_handler(self, users: list, keys: list) -> dict:
        shardedhandlers = {}
        shardedusers = self.shard_list(users, keys)
        for index, batch in enumerate(await shardedusers):
            keybatch: dict = keys[index]
            shardedhandlers.update(
                {
                    TwitterHandler(
                        consumer_key=keybatch['twitter_api_key'],
                        consumer_secret=keybatch['twitter_api_secret'],
                        access_token=keybatch['twitter_access_token'],
                        access_token_secret=keybatch['twitter_access_token_secret'],
                        return_type=dict,
                        wait_on_rate_limit=False
                    ): batch
                }
            )

        return shardedhandlers

    async def run_shards(self) -> dict:
        difference = {}
        differences = await asyncio.gather(*[
            handler.check_users(batch) for handler, batch in self.sharded_handler.items()
        ])

        for dict in differences:
            difference.update(dict)

        return difference

    async def create_shards(self, users: list, keys: list):
        self.sharded_handler = await self.shard_handler(users, keys)
