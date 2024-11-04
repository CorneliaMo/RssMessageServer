from flask import Flask, send_file, request, abort
from json import loads, dumps
from random import randint
from xmlGenerator import genXML
from os.path import exists
from waitress import serve
from time import localtime, strftime

app = Flask(__name__)


@app.route("/<int:channelId>/<int:itemId>")
def rssItem(channelId, itemId):
    print(strftime("%Y-%m-%d %H:%M:%S", localtime())+"  "+request.headers.get("X-Real-Ip")+" get page")
    with open('rss.json', mode='r') as f:
        rssJson = loads(f.readline())
    for channel in rssJson["channel"]:
        if channel["id"] == channelId:
            for item in channel["item"]:
                if item["id"] == itemId:
                    return item["description"]
    abort(404)


@app.route("/<int:channelId>")
def rssChannel(channelId):
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " get page")
    with open('rss.json', mode='r') as f:
        rssJson = loads(f.readline())
    for channel in rssJson["channel"]:
        if channel["id"] == channelId:
            return channel["description"]
    abort(404)


@app.route("/")
def rssSubscribe():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " update rss")
    if not exists('rss.xml'):
        genXML()
    return send_file("rss.xml")


@app.route("/addChannel", methods=["POST"])
def addChannel():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " add channel")
    postJson = loads(request.get_data())
    with open('rss.json', mode='r') as f:
        rssJson = loads(f.readline())
    channelId = len(rssJson["channel"])+1
    newChannel = {}
    if "title" not in postJson or "description" not in postJson:
        abort(500)
    for element in postJson.items():
        newChannel[element[0]] = element[1]
    newChannel["id"] = channelId
    newChannel["item"] = []
    newChannel["link"] = "https://server.corneliamo.cn:10100/rss/"+str(channelId)
    rssJson["channel"].append(newChannel)
    with open('rss.json', mode='w') as f:
        f.write(dumps(rssJson))
    genXML()
    return {"id": channelId}


@app.route("/addMessage", methods=["POST"])
def addMessage():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " add message")
    postJson = loads(request.get_data())
    if "title" not in postJson or "description" not in postJson or "id" not in postJson:
        abort(500)
    with open("rss.json", mode='r') as f:
        rssJson = loads(f.readline())
    channelId = postJson["id"]
    if not isinstance(channelId, int):
        return "id should be int", 500
    for i in range(len(rssJson["channel"])):
        if rssJson["channel"][i]["id"] == channelId:
            messageId = len(rssJson["channel"][i]["item"])+1
            newItem = {}
            for element in postJson.items():
                newItem[element[0]] = element[1]
            newItem["id"] = messageId
            newItem["link"] = "https://server.corneliamo.cn:10100/rss/" + str(channelId) + "/" + str(messageId)
            rssJson["channel"][i]["item"].append(newItem)
            with open('rss.json', mode='w') as f:
                f.write(dumps(rssJson))
            genXML()
            return {"id": messageId}
    abort(500)


@app.route("/modifyChannel", methods=["POST"])
def modifyChannel():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " modify channel")
    postJson = loads(request.get_data())
    if "id" not in postJson:
        abort(500)
    channelId = postJson["id"]
    if not isinstance(channelId, int):
        return "id should be int", 500
    with open("rss.json", mode='r') as f:
        rssJson = loads(f.readline())
    for i in range(len(rssJson["channel"])):
        if rssJson["channel"][i]["id"] == channelId:
            for element in postJson.items():
                if element[0] != "item" and element[0] != "id" and element[0] != "link":
                    rssJson["channel"][i][element[0]] = element[1]
            with open('rss.json', mode='w') as f:
                f.write(dumps(rssJson))
            abort(200)
    abort(500)


@app.route("/modifyMessage", methods=["POST"])
def modifyMessage():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " modify message")
    postJson = loads(request.get_data())
    if "channelId" not in postJson or "messageId" not in postJson:
        return "check if channelId and messageId are submitted", 500
    channelId = postJson["channelId"]
    messageId = postJson["messageId"]
    if not isinstance(channelId, int) or not isinstance(messageId, int):
        return "channelId and messageId should be int", 500
    with open("rss.json", mode='r') as f:
        rssJson = loads(f.readline())
    if channelId<=len(rssJson["channel"]):
            if messageId<=len(rssJson["channel"][channelId-1]["item"]):
                for element in postJson.items():
                    if element[0] != "channelId" and element[0] != "messageId" and element[0] != "id" and element[0] != "link":
                        rssJson["channel"][channelId-1]["item"][messageId-1][element[0]] = element[1]
                with open('rss.json', mode='w') as f:
                    f.write(dumps(rssJson))
                    abort(200)
    abort(500)


@app.route("/deleteChannel", methods=["POST"])
def deleteChannel():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " delete channel")
    postJson = loads(request.get_data())
    if "id" not in postJson:
        return "Check if id is submitted", 500
    channelId = postJson["id"]
    if not isinstance(channelId, int):
        return "id should be int", 500
    with open('rss.json', mode='r') as f:
        rssJson = loads(f.readline())
    if id<=len(rssJson["channel"]):
        del rssJson["channel"][channelId-1]
        for i in range(channelId-1, len(rssJson["channel"])):
            rssJson["channel"][i]["id"] = rssJson["channel"][i]["id"]-1
        with open('rss.json', mode='w') as f:
            f.write(dumps(rssJson))
            abort(200)
    abort(500)


@app.route("/deleteMessage", methods=["POST"])
def deleteMessage():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " delete message")
    postJson = loads(request.get_data())
    if "channelId" not in postJson or "messageId" not in postJson:
        return "Check if channelId and messageId are submitted", 500
    channelId = postJson["channelId"]
    messageId = postJson["messageId"]
    if not isinstance(channelId, int) or not isinstance(messageId, int):
        return "channelId and messageId should be int", 500
    with open('rss.json', mode='r') as f:
        rssJson = loads(f.readline())
    if channelId<=len(rssJson["channel"]):
        if messageId<=len(rssJson["channel"][channelId]["item"]):
            del rssJson["channel"][channelId-1]["item"][messageId]
            for i in range(messageId-1, len(rssJson["channel"][channelId]["item"])):
                rssJson["channel"][channelId-1]["item"][i]["id"] = rssJson["channel"][channelId-1]["item"][i]["id"] - 1
            with open('rss.json', mode='w') as f:
                f.write(dumps(rssJson))
                abort(200)
    abort(500)


@app.route("/getMessageList", methods=["POST"])
def getMessageList():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " get message list")
    postJson = loads(request.get_data())
    if "id" not in postJson:
        abort(500)
    channelId = postJson["id"]
    if not isinstance(channelId, int):
        return "id should be int", 500
    with open("rss.json", mode='r') as f:
        rssJson = loads(f.readline())
    for channel in rssJson["channel"]:
        if channel["id"] == channelId:
            return channel["item"]
    abort(500)


@app.route("/getChannelList")
def getChannelList():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " get channel list")
    with open('rss.json', mode='r') as f:
        rssJson = loads(f.readline())
    channelList = []
    for channel in rssJson["channel"]:
        del channel["item"]
        channelList.append(channel)
    return channelList


if __name__ == "__main__":
    if not exists("rss.json"):
        with open('rss.json', 'w') as f:
            f.write("{\"channel\": []}")
    print("server start")
    serve(app, host='127.0.0.1', port=5002)
