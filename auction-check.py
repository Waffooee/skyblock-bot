import datetime
import json
import re
import time

import discord
import requests

# APIキーはBOTの管理者のもののみでOK
api_key = "BOT Owner's API key"


def get_endpoint_url(name, profile_name, endpoint):
    url = str("https://api.hypixel.net/player?key=" + api_key + "&name=" + name)
    headers = {"content-type": "application/json"}
    r = requests.get(url, headers=headers)
    data = r.json()
    profiles = (data["player"]["stats"]["SkyBlock"]["profiles"])
    for profs in profiles.values():
        if (profs["cute_name"]) == profile_name:
            url = str("https://api.hypixel.net/" + endpoint + "?key=" + api_key + "&name=" + name + "&profile=" + str(
                profs["profile_id"]))
            return url


def get_my_auctions(name, profile_name):
    endpoint = "skyblock/auction"
    total_coins = 0
    results = []
    url = get_endpoint_url(name, profile_name, endpoint)
    headers = {"content-type": "application/json"}
    r = requests.get(url, headers=headers)
    data = r.json()
    my_auctions = list(data["auctions"])
    for unclaimed in my_auctions:
        if not (unclaimed["claimed"]):
            item = str(unclaimed["item_name"])
            end = int(((unclaimed["end"]) // 1000) - time.time())
            bid = int(unclaimed["highest_bid_amount"])
            delta = datetime.timedelta(seconds=int(end))
            delta_m, deltas = divmod(delta.seconds, 60)
            delta_h, delta_m = divmod(delta_m, 60)
            delta_d = delta.days
            high_bid = "{:,}".format(bid)
            if end > 0:
                result = str(
                    ":arrows_counterclockwise: " + "アイテム: " + item + "\n" + "　 終了まで: " + str(delta_d) + "日 " + str(
                        delta_h) + "時間" + str(delta_m) + "分 " + str(deltas) + "秒 " + "\n" + "　 最高bid: " + (
                        high_bid) + "coin")
                total_coins = total_coins + bid
            else:
                if int(unclaimed["highest_bid_amount"]) == 0:
                    result = str(":warning: " + "アイテム: " + item + "\n" + "　 終了済み" + "\n" + "　 bid無し")
                else:
                    result = str(":white_check_mark: " + "アイテム: " + item + "\n" + "　 終了済み" + "\n" + "　 最高bid: " + (
                        high_bid) + "coin")
                    total_coins = total_coins + bid
            results.append(result)
        return results, total_coins


def add_new_usr(author, name, profile_name):
    new_file = "usrdata/" + author + ".json"
    with open(new_file, "w") as nf:
        data = {"name": str(name), "profile": str(profile_name)}
        json.dump(data, nf, ensure_ascii=False)
        return name, profile_name


class MyClient(discord.Client):

    async def on_ready(self):
        return

    async def on_message(self, message):
        if message.author == self.user:
            return

        if re.compile("!ah").search(message.content):
            author = str(message.author.id)
            try:
                usrdata = "usrdata/" + author + ".json"
                f = open(usrdata)
                usr = json.load(f)
                key = str(usr["key"])
                name = str(usr["name"])
                if re.match("(!ah )(.*)", message.content):
                    arg = re.match("(!ah )(.*)", message.content).group(2).capitalize()
                    profile_name = str(arg)
                else:
                    profile_name = str(usr["profile"])
                get_my_auctions(name, profile_name)
                results, total_coins = get_my_auctions(name, profile_name)
                if len(results) == 0:
                    await message.channel.send(
                        message.author.mention + "\n" + ":information_source: " + "未回収のオークションはありません")
                    pass
                else:
                    txt = "\n".join(results)
                    total_coins = "{:,}".format(total_coins)
                    await message.channel.send(
                        message.author.mention + "\n" + "未回収のオークションがあります。" + "\n" + txt + "\n" + "　**売上総額: " + (
                            total_coins) + "coin**")
                    pass
            except KeyError:
                await message.channel.send(message.author.mention + "\n" + ":warning: " + "キーエラー" + "\n" + "APIキーが不正です")
            except FileNotFoundError:
                msg1 = "アクセス情報が登録されていません"
                msg2 = "```!add (MCID) (プロファイル名)```"
                msg3 = "の形でアクセス情報を登録してください"
                msg4 = "プロファイル名は基本的に果物の名前です。ゲーム内コマンド`/profiles`から確認できます"
                msg5 = "```例：!add hisuie08 Mango```"
                await message.channel.send(
                    message.author.mention + "\n" + msg1 + "\n" + msg2 + "\n" + msg3 + "\n" + msg4 + "\n" + msg5 + "\n")
            return

        if re.compile("(!add )(.+)([ ,])(.+)([ ,])(.+)").match(message.content):
            author = str(message.author.id)
            com = re.match("(!add )(.+)([ ,])(.+)([ ,])(.+)", message.content)
            name = com.group(2)
            profile_name = com.group(4).capitalize()
            msg = "登録を完了しました。"
            new_name, new_profile = add_new_usr(author, name, profile_name)
            await message.channel.send(
                message.author.mention + msg + "\n" + "\n" + "MCID:" + str(
                    new_name) + "\n" + "プロファイル:" + str(new_profile))
            return


client = MyClient()
token = "TOKEN"
client.run(token)
