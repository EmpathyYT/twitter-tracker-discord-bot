# Here are the changes I made that you need to know about:
- Your were using an old version of `DPY(1.5.1)`, which is outdated, so I upgraded to `2.1`
- Your were using an old version of `TWEEPY(2.9.0)`, which is outdated, so I upgraded to `4.12.1`
- You were miss using the Twitter API
- You included `AIOHTTP` in the `requirements` file, that's not required, since it gets installed by default with `DPY`
- ***DO NOT*** update the config while the bot is running
- Commented out the Latest Tweet part `(main.py)`, since it requires elevated access
- Changed the `discord_channel_id` attribute in `config.json` from type `STR` to type `INT`, since this is what the method expects
- I added the `dateutil` package to the `requirements` file to covert datetimes
- I reset the `token` and `user_id` lists
- This app uses a sharding mechanism; it divides the calls into different keys to reduce load and avoid rate limits
- `main.py` is the launcher, not the bot.
- make sure you're on python version >= `3.10`
- added the library `async_lru`
- switched twitter handler from synchronous to asynchronous
- bot uses the most amount of keys possible to reduce load, if you provide enough keys we would be able to reduce the time every 2 revolutions.


# How to run:
## Run these commands in the terminal of your workspace
- `py -m venv venv`
- `venv\Scripts\activate`
- `pip install -r requirements.txt`

### Happy stalking ;)