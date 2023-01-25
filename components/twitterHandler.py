import asyncio

import tweepy.asynchronous
import json

with open("./components/config.json") as f:
    config = json.load(f)


class TwitterHandler(tweepy.asynchronous.AsyncClient):
    def __init__(self, bearer_token=None, consumer_key=None, consumer_secret=None, access_token=None,
                 access_token_secret=None, *, return_type=..., wait_on_rate_limit=False):
        super().__init__(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret,
                         return_type=return_type, wait_on_rate_limit=wait_on_rate_limit)
        self.userDict = {}
        self.runs = 0
        self.auth = tweepy.OAuthHandler(consumer_key=consumer_key, consumer_secret=consumer_secret,
                                        access_token=access_token, access_token_secret=access_token_secret)
        self.api = tweepy.API(self.auth)
        self.userlist = []

    async def loop_over_response(self, user, response: dict) -> list:
        listfollow = []
        for followingUser in response['data']:
            listfollow.append(followingUser)

        if "next_token" in response['meta'].keys():
            listfollow.extend(
                await self.loop_over_response(
                    user, await super().get_users_following(user, max_results=1000,
                                                            user_fields=['created_at', 'username', 'public_metrics',
                                                                         'profile_image_url'],
                                                            pagination_token=response['meta']['next_token'],
                                                            user_auth=True)
                )
            )
        return listfollow

    async def check_users(self, users: list) -> dict:
        newdict = {}
        difference = {}
        for user in users:
            try:
                response = await super().get_users_following(user, max_results=1000,
                                                            user_fields=['created_at', 'username', 'public_metrics',
                                                                        'profile_image_url'], user_auth=True)
                # list of user dicts
                newdict[user] = await self.loop_over_response(user, response)
            except Exception as e:
                print(e)
                return
                
        

        if self.runs != 0:
            for user, follwingList in newdict.items():
                difference[user] = []
                for followingUser in follwingList:
                    if followingUser['id'] not in [following['id'] for following in self.userDict[user]]:
                        difference[user].append(followingUser)  # he's new
        self.runs += 1
        self.userDict = newdict
        return difference
