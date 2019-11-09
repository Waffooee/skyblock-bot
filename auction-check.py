import asyncio
import datetime
import json
import os
import re
import time
import discord
import requests


def getendpointurl(key, name, profilename, endpoint):  #APIｴﾝﾄﾞﾎﾟｲﾝﾄ取得関数
    url = str("https://api.hypixel.net/player?key=" + (key) + "&name=" + (name))
    headers = {"content-type": "application/json"}
    r = requests.get(url, headers=headers)
    data = r.json()
    profiles = (data["player"]["stats"]["SkyBlock"]["profiles"])
    for profs in profiles.values():  #SBのｴﾝﾄﾞﾎﾟｲﾝﾄの取得にはﾌﾟﾛﾌｧｲﾙ名ではなくﾌﾟﾛﾌｧｲﾙIDっていうのを使うらしく二度手間()
        if (profs["cute_name"]) == profilename:
            url = str("https://api.hypixel.net/" + (endpoint)+  "?key=" + (key) + "&name=" + (name) + "&profile=" + str(profs["profile_id"]))
            return url

def getmyauction(key, name, profilename):  #ｵｰｸｼｮﾝ取得関数。MyClientｸﾗｽのon_messageで!ahｺﾏﾝﾄﾞが打たれたのを検知したら呼び出されます
    endpoint = "skyblock/auction"
    url = getendpointurl(key, name,profilename, endpoint)
    headers = {"content-type": "application/json"}
    r = requests.get(url, headers=headers)
    data = r.json()
    myauction = list(data["auctions"])  #ここでまずｵｰｸｼｮﾝを全部洗い出し
    totalcoins = 0
    results = []
    for unclaimed in myauction:
        if (unclaimed["claimed"]) == False:  #回収されていないものを選別
            item = str(unclaimed["item_name"])
            end = int(((unclaimed["end"]) // 1000) - time.time())  #ﾊｲﾋﾟAPIでは時刻はUNIXｴﾎﾟｯｸ時間のﾐﾘ秒で提供されるので秒に揃えて現在の時間との差分を算出
            bid = int(unclaimed["highest_bid_amount"])
            delta = datetime.timedelta(seconds=int(end))  #UNIXｴﾎﾟｯｸ時間の単位は秒だから脳死割り算で時間、分を出せる便利。日だけは別で渡されるのを知らなかった…
            deltam, deltas = divmod(delta.seconds, 60)  #分
            deltah, deltam = divmod(deltam, 60)  #時間
            deltad = delta.days  #日 ここでtimedeltaの戻り値の型をろくに調べないで脳死で//24した私はﾊﾞｸﾞらせました（）
            highbid = "{:,}".format(bid)
            if end > 0:  #ここからはbidの状態判定。まず終了しているかどうか
                result = str(":arrows_counterclockwise: " + "アイテム: " + (item) + "\n" + "　 終了まで: " + str(deltad) + "日 " + str(deltah) + "時間" + str(deltam) + "分 " + str(deltas) + "秒 " + "\n" + "　 最高bid: " + (highbid) + "coin")
                totalcoins = totalcoins + bid
            else:
                if int(unclaimed["highest_bid_amount"]) == 0:  #終了していればbidの有無を判定してそれぞれ出力するﾒｯｾｰｼﾞに入れ込みます
                    result = str(":warning: " +"アイテム: " + (item) + "\n" + "　 終了済み" + "\n" + "　 bid無し")
                else:
                    result = str(":white_check_mark: " + "アイテム: " + (item) + "\n" + "　 終了済み" + "\n" + "　 最高bid: " + (highbid) + "coin")
                    totalcoins = totalcoins + bid
            results.append(result)
    return results,totalcoins

def addnewusr(author,key,name,profilename):  #新規ﾕｰｻﾞｰ追加
    newfile = "usrdata/"+(author)+".json"  #DiscordのﾕﾆｰｸIDをﾌｧｲﾙ名にしてAPIｷｰ、MCID、ﾌﾟﾛﾌｧｲﾙ名をjson格納という至ってｼﾝﾌﾟﾙな管理なんだけど、これだとﾏﾙﾁﾌﾟﾛﾌｧｲﾙに対応できない悲しみ
    with open(newfile, "w") as nf:
        data = {"key": str(key), "name": str(name), "profile": str(profilename)}
        json.dump(data, nf, ensure_ascii=False)
        return key, name, profilename  #登録情報を確認するために書き込んだ情報をreturnします

class MyClient(discord.Client):

    async def on_ready(self):  #ここにｹﾞｰﾑ内ｲﾍﾞﾝﾄの通知機能を入れ込む予定
        return

    async def on_message(self, message)  :#ﾒｯｾｰｼﾞ監視関数
        if message.author == self.user:
            return

        if re.compile("!ah").match(message.content):  #ｺﾏﾝﾄﾞを検知
            author = str(message.author.id)  #ﾕｰｻﾞｰのﾕﾆｰｸIDを取得
            try:  #登録情報を確認します
                usrdata = "usrdata/"+(author)+".json"
                f = open(usrdata)
                usr = json.load(f)
                key = str(usr["key"])
                name = str(usr["name"])
                profilename = str(usr["profile"])
                getmyauction(key, name, profilename)
                results,totalcoins = getmyauction(key, name, profilename)
                if len(results) == 0:        
                    await message.channel.send(message.author.mention + "\n" +":information_source: "+"未回収のオークションはありません")
                    pass
                else:
                    txt = "\n".join(results)
                    totalcoins = "{:,}".format(totalcoins)
                    await message.channel.send(message.author.mention + "\n"+"未回収のオークションがあります。" + "\n" + (txt) + "\n" + "　**売上総額: " + (totalcoins)+"coin**")
                    pass
            except KeyError:
                await message.channel.send(message.author.mention + "\n" + ":warning: " + "キーエラー" + "\n" + "APIキーが不正です")
            except FileNotFoundError:  #FileNotFoundErrorと未登録を安易に同値とできるあたりこの管理形式は天才だと思った(小並
                msg1 = "アクセス情報が登録されていません"
                msg2 = "!add (APIキー) (MCID) (プロファイル名)"
                msg3 = "の形でアクセス情報を登録してください"
                msg4 = "APIキーはゲーム内で/api または/api new で取得できます"
                msg5 = "プロファイル名はゲーム内で/profilesと入力して表示される果物の名前です"
                await message.channel.send(message.author.mention + "\n" + msg1 + "\n" + msg2 + "\n" + msg3 + "\n" + msg4 + msg5)
            return

        if re.compile("(!add )(.+)( |,)(.+)( |,)(.+)").match(message.content):  #!addｺﾏﾝﾄﾞで打たれた内容を切り分けて登録する。単純な正規表現です
            author = str(message.author.id)
            com = re.match("(!add )(.+)( |,)(.+)( |,)(.+)", message.content)
            key = com.group(2)
            name = com.group(4)
            profilename = com.group(6).capitalize()  #プロファイル名最初が大文字でなくても自動で大文字にして登録するようにしました
            msg = "登録を完了しました。"
            newkey,newname,newprofile = addnewusr(author,key,name,profilename)
            await message.channel.send(message.author.mention + (msg) +"\n"+"キー:"+str(newkey)+"\n"+"MCID:"+str(newname)+"\n"+"プロファイル:"+str(newprofile))
            return
            

client = MyClient()
token = ("TOKEN")
client.run(token)
