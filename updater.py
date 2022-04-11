from json_db import JSON_DB
from aiohttp import ClientSession
import xmltodict
import asyncio
import itertools
from typing import Any
from nextcord import Client, TextChannel


def start(loop, db: JSON_DB, client):
    update_feeds(loop, db, client)


def schedule_update(loop, db: JSON_DB, client):
    loop.call_later(5*60, update_feeds, loop, db, client)
    print("Scheduled the next feed update")


def update_feeds(loop, db: JSON_DB, client):
    schedule_update(loop, db, client)
    loop.create_task(do_feed_update(db, client))


async def do_feed_update(db: JSON_DB, client):
    print("Doing feed update")
    for guild_id, feeds in db.get("feeds", default={}).items():
        print(f"Updating feeds for guild ID {guild_id}")
        await do_guild_feed_updates(guild_id, feeds, db, client)


async def do_guild_feed_updates(guild_id: str, feeds: list[str], db: JSON_DB, client):
    await asyncio.gather(*[update_feed(guild_id, feed_url, db, client) for feed_url in feeds])


async def update_feed(guild_id: str, feed_url: str, db: JSON_DB, client):
    feed_data = await get_latest_feed(feed_url)
    if feed_data:
        last_seen_guid = get_last_seen_item_guid(guild_id, feed_url, db)
        current_guid = feed_data[0]["guid"]["#text"]
        if last_seen_guid != current_guid:
            new_items = get_new_items_from_feed(feed_data, last_seen_guid)
            for item in new_items:
                await handle_new_item(item, guild_id, db, client)

                if last_seen_guid is None:
                    break

            save_new_guid(current_guid, guild_id, feed_url, db)


async def handle_new_item(item: dict, guild_id: str, db: JSON_DB, client):
    channel = get_guild_feed_update_channel(db, guild_id, client)
    if channel:
        await channel.send(f"**New Episode**\n{item['title']}\n{item['link']}")


async def get_latest_feed(feed_url: str) -> list[dict[str, Any]]:
    async with ClientSession() as session:
        async with session.get(feed_url) as response:
            print(f"Loaded {feed_url}")
            return xmltodict.parse(await response.content.read())["rss"]["channel"].get("item", [])


def get_new_items_from_feed(feed_data: list[dict], last_seen_guid: str) -> list[dict]:
    items = []
    for item in itertools.islice(feed_data, 5):
        if item["guid"]["#text"] != last_seen_guid:
            items.append(item)

    return items


def get_guild_feed_update_channel(db: JSON_DB, guild_id: str, client: Client) -> TextChannel:
    channel_id = db.get("guilds", default={}).get(guild_id, None)
    if channel_id:
        return client.get_channel(channel_id)


def get_last_seen_item_guid(guild_id: str, feed_url: str, db: JSON_DB) -> str | None:
    guilds = db.get("items", default={})
    feeds = guilds.get(guild_id, {})
    guid = feeds.get(feed_url, None)
    return guid


def save_new_guid(new_guid: str, guild_id: str, feed_url: str, db: JSON_DB):
    guilds = db.get("items", default={})
    feeds = guilds.get(guild_id, {})
    feeds[feed_url] = new_guid
    guilds[guild_id] = feeds
    db.set("items", guilds)
