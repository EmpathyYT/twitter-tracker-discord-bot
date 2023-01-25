# Be aware of the following notes:
- ***DO NOT*** update the config while the bot is running
- Commented out the Latest Tweet part `(main.py)`, since it requires elevated access
- Changed the `discord_channel_id` attribute in `config.json` from type `STR` to type `INT`, since this is what the method expects
- This app uses a sharding mechanism; it divides the calls into different keys to reduce load and avoid rate limits
- `main.py` is the launcher, not the bot.
- make sure you're on python version >= `3.10`
- bot uses the most amount of keys possible to reduce load, if you provide enough keys you would be able to reduce the time every 2 revolutions.
- for every key, you can index nearly 15k users.

# How to run:
## Run these commands in the terminal of your workspace
- `py -m venv venv`
- `venv\Scripts\activate`
- `pip install -r requirements.txt`

### Happy stalking ;)
