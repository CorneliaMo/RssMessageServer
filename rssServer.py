"""
Since I use nginx to relay http requests, the headers include "X-Real-Ip" indicates the real source.
If you directly access the http api or "X-Real-Ip" is no included in the headers,
    please modify the debug messages at the beginning of each function or disable them.
Otherwise, script will throw exception because loading specific header failed.

CorneliaMo, 2024-11-5
"""

from flask import Flask, send_file, request, abort
from json import loads, dumps
from xmlGenerator import genXML
from os.path import exists
from waitress import serve
from time import localtime, strftime

app = Flask(__name__)


@app.route("/<int:channelId>/<int:itemId>")
# Page for single message
def rssItem(channelId, itemId):
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " get page")
    with open('rss.json', mode='r') as f:
        rssJson = loads(f.readline())
    for channel in rssJson["channel"]:
        if channel["id"] == channelId:
            for item in channel["item"]:
                if item["id"] == itemId:
                    return item["description"]
    return "Message not found", 404


@app.route("/<int:channelId>")
# Page for single channel
def rssChannel(channelId):
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " get page")
    with open('rss.json', mode='r') as f:
        rssJson = loads(f.readline())
    for channel in rssJson["channel"]:
        if channel["id"] == channelId:
            return channel["description"]
    return "Channel not found", 404


@app.route("/")
# Return the xml file for rss
def rssSubscribe():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " update rss")
    if not exists('rss.xml'):
        genXML()
    return send_file("rss.xml")


@app.route("/addChannel", methods=["POST"])
# POST {"title": titleString, "description": descriptionString}
# Provide title and description to create a new channel
# Return id for the new channel
# Return {"id": newChannelId}
def addChannel():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " add channel")
    postJson = loads(request.get_data())
    if "title" not in postJson or "description" not in postJson:
        return "check if title and description are submitted", 500
    with open('rss.json', mode='r') as f:
        rssJson = loads(f.readline())
    channelId = 1 if len(rssJson["channel"]) == 0 else rssJson["channel"][-1]["id"]+1
    newChannel = {}
    for element in postJson.items():
        newChannel[element[0]] = element[1]
    newChannel["id"] = channelId
    newChannel["item"] = []
    newChannel["link"] = "https://server.corneliamo.cn:10100/rss/" + str(channelId)
    rssJson["channel"].append(newChannel)
    with open('rss.json', mode='w') as f:
        f.write(dumps(rssJson))
    genXML()
    return {"id": channelId}


@app.route("/addMessage", methods=["POST"])
# POST {"id": existChannelId, "title": messageTitle, "description": message}
# Provide an exist channel id, title and description to publish a new message
# Return id for the new message
# Return {"id": newMessageId}
def addMessage():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " add message")
    postJson = loads(request.get_data())
    if "title" not in postJson or "description" not in postJson or "id" not in postJson:
        return "check if title, description and id are submitted", 500
    channelId = postJson["id"]
    if not isinstance(channelId, int):
        return "id should be int", 500
    with open("rss.json", mode='r') as f:
        rssJson = loads(f.readline())
    for i in range(len(rssJson["channel"])):
        if rssJson["channel"][i]["id"] == channelId:
            messageId = 1 if len(rssJson["channel"][i]["item"]) == 0 else rssJson["channel"][i]["item"][-1]["id"] + 1
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
# POST {"id": existChannelId, ...kwargs}
# Provide an exist channel id and cover channel properties using kwargs (except id, item, and link)
# Return 200 if success
def modifyChannel():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " modify channel")
    postJson = loads(request.get_data())
    if "id" not in postJson:
        return "check if id is submitted"
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
            genXML()
            abort(200)
    abort(500)


@app.route("/modifyMessage", methods=["POST"])
# POST {"channelId": existChannelId, "messageId": existMessageId, ...kwargs}
# Provide exist channel id and exist message id, cover message properties using kwargs (except id and link)
# Return 200 if success
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
    for channelQuery in range(len(rssJson["channel"])):
        if channelId == rssJson["channel"][channelQuery]["id"]:
            for itemQuery in range(rssJson["channel"][channelQuery]["item"]):
                if messageId == rssJson["channel"][channelQuery]["item"][itemQuery]["id"]:
                    for element in postJson.items():
                        if element[0] != "channelId" and element[0] != "messageId" and element[0] != "id" and element[0] != "link":
                            rssJson["channel"][channelQuery]["item"][itemQuery][element[0]] = element[1]
                    with open('rss.json', mode='w') as f:
                        f.write(dumps(rssJson))
                    genXML()
                    abort(200)
    abort(500)


@app.route("/deleteChannel", methods=["POST"])
# POST {"id": existChannelId}
# Provide an exist channel id, delete the corresponding channel include its messages
# Return 200 if success
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
    for channelQuery in range(len(rssJson["channel"])):
        if channelId == rssJson["channel"][channelQuery]["id"]:
            del rssJson["channel"][channelQuery]
            with open('rss.json', mode='w') as f:
                f.write(dumps(rssJson))
            genXML()
            abort(200)
    abort(500)


@app.route("/deleteMessage", methods=["POST"])
# POST {"channelId": existChannelId, "messageId": existMessageId}
# Provide exist channel id and exist message id, delete the corresponding message
# Return 200 if success
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
    for channelQuery in range(len(rssJson["channel"])):
        if channelId == rssJson["channel"][channelQuery]["id"]:
            for messageQuery in range(len(rssJson["channel"][channelQuery]["item"])):
                if messageId == rssJson["channel"][channelQuery]["item"][messageQuery]["id"]:
                    del rssJson["channel"][channelQuery]["item"][messageQuery]
                    with open('rss.json', mode='w') as f:
                        f.write(dumps(rssJson))
                    genXML()
                    abort(200)
    abort(500)


@app.route("/getMessageList", methods=["POST"])
# POST {"id": existChannelId}
# Provide an exist channel id, return a list for messages in the channel
# Return all json data of messages, code 500 if query fail
def getMessageList():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " get message list")
    postJson = loads(request.get_data())
    if "id" not in postJson:
        return "Check if id is submitted", 500
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
# Directly access
# Return all json data of channels except "item" data
def getChannelList():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()) + "  " + request.headers.get("X-Real-Ip") + " get channel list")
    with open('rss.json', mode='r') as f:
        rssJson = loads(f.readline())
    channelList = []
    for channel in rssJson["channel"]:
        # avoid to return tedious information
        del channel["item"]
        channelList.append(channel)
    return channelList


if __name__ == "__main__":
    # Initialize the json file to store channels and messages
    if not exists("rss.json"):
        with open('rss.json', 'w') as f:
            f.write("{\"channel\": []}")
    print("server start")
    serve(app, host='127.0.0.1', port=5002)
