# Discord Bot: RSS Feed Reader

This is a simple bot that monitors RSS feeds and announces when new items show up in the feeds.

## Live Stream

Watch the video of me building this bot start to finish on [YouTube!!!](https://youtu.be/RCAJie1rmvU?t=1741)

## Running

Create a file named `token.secret` and put your Discord bot token in that file. Next run the following commands:
```shell
pip install poetry
poetry install
poetry run python bot.py
```

## Commands

`rss!add [url to RSS feed]`

This will add an RSS feed to the bot for the current guild.

`rss!remove [url to RSS feed]`

This will remove an RSS feed from the bot for the current guild.

`rss!list`

This will list all of the RSS feeds that the bot is monitoring for the current guild.

`rss!setup [text channel]`

This will tell the bot which channel to announce new RSS feed items in. This must be run before the bot will function in a guild.

`rss!info`

Shows which channel the bot is set to use for new RSS feed item announcements.
