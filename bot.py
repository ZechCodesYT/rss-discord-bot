from nextcord.ext.commands import Bot, Context
from nextcord import Intents, TextChannel
from contextlib import ExitStack
from json_db import JSON_DB
from updater import start


intents = Intents.default()
intents.messages = True


class RSSBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.updates_scheduled = False


client = RSSBot(intents=intents, command_prefix="rss!")


@client.listen()
async def on_ready():
    if not client.updates_scheduled:
        start(client.loop, db, client)

    print("We're alive!!!")


@client.command()
async def add(ctx: Context, feed_url: str):
    guilds = db.get("feeds", default={})
    feeds = guilds.get(str(ctx.guild.id), [])

    feeds.append(feed_url)

    guilds[str(ctx.guild.id)] = feeds
    db.set("feeds", guilds)

    await ctx.send(f"Added `{feed_url}` to the {ctx.guild.name} feed list")


@client.command()
async def remove(ctx: Context, feed_url: str):
    guilds = db.get("feeds", default={})
    feeds = guilds.get(str(ctx.guild.id), [])

    try:
        feeds.remove(feed_url)
    except ValueError:
        await ctx.send(f"`{feed_url}` was already removed from the {ctx.guild.name} feed list")
    else:
        guilds[str(ctx.guild.id)] = feeds
        db.set("feeds", guilds)

        await ctx.send(f"Removed `{feed_url}` to the {ctx.guild.name} feed list")


@client.command(name="list")
async def list_command(ctx: Context):
    guilds = db.get("feeds", default={})
    feeds = guilds.get(str(ctx.guild.id), [])
    feed_list = "\n".join(feeds) if feeds else "*No Feeds Found*"
    await ctx.send(f"**Feed List**\n{feed_list}")


@client.command()
async def setup(ctx: Context, channel: TextChannel):
    guilds = db.get("guilds", default={})
    guilds[str(channel.guild.id)] = channel.id
    db.set("guilds", guilds)
    await ctx.send(f"Successfully set {channel.mention} as the RSS feed channel")


@client.command()
async def info(ctx: Context):
    channel_id = db.get("guilds", default={}).get(str(ctx.guild.id), None)
    channel = ctx.guild.get_channel(channel_id).mention if channel_id is not None else "*Not Set*"
    await ctx.send(f"The RSS feed channel for {ctx.guild.name} is {channel}")


with ExitStack() as stack:
    stack.enter_context(token_file := open("token.secret"))
    stack.enter_context(db := JSON_DB(__file__))
    client.run(token_file.read().strip())
