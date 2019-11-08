import asyncio
import datetime
import json
import time
import requests
import discord

#Before you run this code, Make sure that you already add roles named "New Years Event", "Spooky Festival", "Magma Boss", "Dark Auction", "Bank Interest" 
# and been enabled mention to them. 
channels = []#This code works on multi channels. Write channel's id you want to notice to down here
async def getevents(eventname, url, noticetime):
    while True:
        data = requests.get(str(url), headers={"content-type": "application/json"}).json()
        eventdelta = int(((data["estimate"]) // 1000) - time.time())
        noticetime = int(noticetime)
        for d in range(eventdelta, -1, -1):
            await asyncio.sleep(1)
            if d > 10800:
                if d % 3600 == 0:#Fix to timerag
                    break
            elif (noticetime - 10) <= d <= (noticetime + 10):
                await asyncio.sleep(60)
                for channel in channels:
                    channel = client.get_channel(channel)
                    role = discord.utils.get(channel.guild.roles, name=eventname)
                    try:
                        await channel.send(f'{role.mention} The event **{eventname}** will come {str(noticetime // 60)}minute later!')
                    except AttributeError:
                        return
                break
            elif d == 0:
                await asyncio.sleep(300)
                break

class MyClient(discord.Client):
    async def on_ready(self):#Thanks to public api for event schedule
        await asyncio.gather(getevents("New Years Event", "https://hypixel-api.inventivetalent.org/api/skyblock/newyear/estimate", 1200)\
        , getevents("Spooky Festival", "https://hypixel-api.inventivetalent.org/api/skyblock/spookyFestival/estimate", 1200)\
        , getevents("Magma Boss", "https://hypixel-api.inventivetalent.org/api/skyblock/bosstimer/magma/estimatedSpawn", 1200)\
        , getevents("Dark Auction", "https://hypixel-api.inventivetalent.org/api/skyblock/darkauction/estimate", 600))\
        , getevents("Bank Interest", "https://hypixel-api.inventivetalent.org/api/skyblock/bank/interest/estimate", 1200)

client = MyClient()
token = ("TOKEN")
client.run(token)
