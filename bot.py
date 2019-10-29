import asyncio
import datetime
import json
import os
import re

import discord
import requests


def getauctionurl(key,name,profilename):
    url = str("https://api.hypixel.net/player?key=" + (key) + "&name=" + (name))
    headers = {"content-type": "application/json"}
    r = requests.get(url, headers=headers)
    data = r.json()
    profiles = (data["player"]["stats"]["SkyBlock"]["profiles"])
    for profs in profiles.values():
        if (profs["cute_name"]) == profilename:
            url = str("https://api.hypixel.net/skyblock/auction?key=" + (key) + "&name=" + (name) + "&profile=" + str(profs["profile_id"]))
            return url

def getmyauction(key, name, profilename):
    results = []
    url = getauctionurl(key, name, profilename)
    headers = {"content-type": "application/json"}
    r = requests.get(url, headers=headers)
    data = r.json()
    myauction = list(data["auctions"])
    for unclaimed in myauction:
        if (unclaimed["claimed"]) == False:
            
            item = str(unclaimed["item_name"])
            end = int((unclaimed["end"]) // 1000)
            endtime = str(datetime.datetime.fromtimestamp(end))
            highbid = str(unclaimed["highest_bid_amount"])
            result = str("アイテム:" + (item) + "　" + "終了:" + (endtime) + "　" + " 最高bid:" + (highbid))
            results.append(result)
    return results

def addnewusr(author,key,name,profilename):
    newfile = "usrdata/"+(author)+".json"
    with open(newfile, "w") as nf:
        data = {"key": str(key), "name": str(name), "profile": str(profilename)}
        json.dump(data, nf, ensure_ascii=False)
    f = open(newfile)
    newusr = json.load(f)
    key = str(newusr["key"])
    name = str(newusr["name"])
    profile = str(newusr["profile"])
    return key, name, profile

class MyClient(discord.Client):

    async def on_ready(self):
        return

    async def on_message(self, message):
        if message.author == self.user:
            return

        if re.compile("!ah").match(message.content):
            author = str(message.author.id)
            try:
                usrdata = "usrdata/"+(author)+".json"
                f = open(usrdata)
                usr = json.load(f)
                key = str(usr["key"])
                name = str(usr["name"])
                profilename = str(usr["profile"])
                getmyauction(key, name, profilename)
                results = getmyauction(key, name, profilename)
                if len(results) == 0:
                    await message.channel.send(message.author.mention + "未回収のオークションはありません")
                    pass
                else:
                    txt = "\n".join(results)
                    await message.channel.send(message.author.mention + "未回収のオークションがあります。" + "\n" + (txt))
                    pass
            except FileNotFoundError:
                msg1 = "アクセス情報が登録されていません。"
                msg2 = "!add (APIキー),(MCID),(プロファイル名)"
                msg3 = "の形でアクセス情報を登録してください。"
                msg4 = "APIキーはゲーム内で/api または/api new で取得できます。"
                await message.channel.send(message.author.mention + "\n" + msg1 + "\n" + msg2 + "\n" + msg3 + "\n" + msg4)
            return

        if re.compile("(!add )(.+)(,)(.+)(,)(.+)").match(message.content):
            author = str(message.author.id)
            com = re.match("(!add )(.+)(,)(.+)(,)(.+)", message.content)
            key = com.group(2)
            name = com.group(4)
            profilename = com.group(6)
            msg = "登録を完了しました。"
            newkey,newname,newprofile = addnewusr(author,key,name,profilename)
            await message.channel.send(message.author.mention + (msg) +"\n"+"キー:"+str(newkey)+"\n"+"MCID:"+str(newname)+"\n"+"プロファイル:"+str(newprofile))
            return
            
            

client = MyClient()
token = ("TOKEN")
client.run(token)