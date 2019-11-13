import datetime
import json
import re
import time

import discord
import requests

# APIキーはBOTの管理者のもののみでOK
api_key = ""


def get_profile_id(name, profile_name):
    url = str("https://api.hypixel.net/player?key=" + api_key + "&name=" + name)
    headers = {"content-type": "application/json"}
    r = requests.get(url, headers=headers)
    data = r.json()
    profiles = (data["player"]["stats"]["SkyBlock"]["profiles"])
    for profs in profiles.values():
        if (profs["cute_name"]) == profile_name:
            return profs["profile_id"]
    raise ValueError


def get_endpoint_url(name, profile_id, endpoint):
    return str("https://api.hypixel.net/" + endpoint + "?key=" + api_key + "&name=" + name + "&profile=" + profile_id)


def get_my_auctions(name, profile_id):
    endpoint = "skyblock/auction"
    total_coins = 0
    results = []
    url = get_endpoint_url(name, profile_id, endpoint)
    headers = {"content-type": "application/json"}
    r = requests.get(url, headers=headers)
    data = r.json()
    my_auctions = list(data["auctions"])
    for unclaimed in my_auctions:
        if unclaimed["claimed"]:
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
    usr = {
        "accounts": {},
        "profiles": []
    }
    try:
        r = open(new_file, "r")
        usr_tmp = json.load(r)
        if "key" in usr_tmp:
            usr, _ = convert_usr_data(author)
        r.close()
    except FileNotFoundError:
        pass

    profile_name = get_profile_id(name, profile_name)
    w = open(new_file, "w")
    usr["accounts"]["default"] = name
    usr["profiles"].append({
        "name": name,
        "profile": profile_name
    })
    json.dump(usr, w)
    w.close()
    return name, profile_name


def get_default_profile(author, name):
    usrdata = "usrdata/" + author + ".json"
    with open(usrdata) as f:
        usr = json.load(f)
        # 'key'が存在する→旧形式でのファイル
        if "key" in usr:
            usr, data_profile = convert_usr_data(author)
            return usr["accounts"]["default"], data_profile
        else:
            profiles = usr["profiles"]
            if name == "":
                name = usr["accounts"]["default"]
            for d in profiles:
                if d["name"].capitalize() == name.capitalize():
                    return name, d["profile"]


def convert_usr_data(author):
    usrdata = "usrdata/" + author + ".json"

    r = open(usrdata, "r")
    usr = json.load(r)
    data_name = usr["name"]
    data_profile = get_profile_id(data_name, usr["profile"])
    r.close()  # with文使うとネスト深くなって嫌だったので普通にclose

    usr = {
        "accounts": {
            "default": data_name
        },
        "profiles": [
            {
                "name": data_name,
                "profile": data_profile
            }
        ]
    }

    w = open(usrdata, "w")
    json.dump(usr, w)
    w.close()
    return usr, data_profile


class MyClient(discord.Client):

    async def on_ready(self):
        return

    async def on_message(self, message):
        if message.author == self.user:
            return

        if re.compile("!ah").search(message.content):
            author = str(message.author.id)
            try:
                name = ""
                profile = ""
                if re.match("(!ah )(.+)([ ,])", message.content):
                    name = str(re.match("(!ah )(.+)([ ,])(.+)", message.content).group(2).capitalize())
                    name, profile = get_default_profile(author, name)
                    if re.match("(!ah )(.+)([ ,])(.+)", message.content):
                        profile = str(re.match("(!ah )(.+)([ ,])(.+)", message.content).group(4).capitalize())

                result, total_coins = get_my_auctions(name, get_profile_id(name, profile))
                if len(result) == 0:
                    await message.channel.send(
                        message.author.mention + "\n" + ":information_source: " + "未回収のオークションはありません")
                    pass
                else:
                    txt = "\n".join(result)
                    total_coins = "{:,}".format(total_coins)
                    await message.channel.send(
                        message.author.mention + "\n" + "未回収のオークションがあります。" + "\n" + txt + "\n" + "　**売上総額: " + total_coins + "coin**")

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

        if re.compile("(!add )(.+)([ ,])(.+)").match(message.content):
            author = str(message.author.id)
            com = re.match("(!add )(.+)([ ,])(.+)", message.content)
            name = com.group(2)
            profile_name = com.group(4).capitalize()
            new_name = ""
            new_profile = ""
            try:
                new_name, new_profile = add_new_usr(author, name, profile_name)
            except ValueError:
                await message.channel.send(message.author.mention + "\n" + "プロファイル名が不正です: " + new_profile)
                return
            msg = "登録を完了しました。"
            await message.channel.send(
                message.author.mention + msg + "\n" + "\n" + "MCID:" + str(
                    new_name) + "\n" + "プロファイル:" + str(new_profile))
            return


client = MyClient()
token = ""
client.run(token)
