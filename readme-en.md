# Message Distribution Service Based on RSS Subscription

[Chinese version](readme.md)

## Idea Origin:
Recently, while maintaining the blog server, I needed to promptly push messages to various administrators when the server was down or other issues occurred, so that problems could be quickly resolved. Initially, I tried private platforms like WeChat and Feishu, but either the APIs were too complex or no interfaces were provided at all. Then I tried email, but emails were likely to be thrown into the spam folder or not pushed to the phone in time. At this point, I thought of RSS subscription, an information aggregation protocol that is not very popular now. It is based on XML, easy to generate and manage, and platform-independent. Any platform can subscribe and receive message pushes with just an RSS reader, hence this project.

## `rssServer.py`:
Implemented based on Flask, it provides an RSS source and HTTP API to add, delete, and modify channels and messages.

## `xmlgenerator.py`:
Converts channels and messages stored in JSON files into XML files for RSS readers.

**The root path "/" provides the XML file for RSS. Fill in the feed link in the RSS reader to subscribe.**

## HTTP API:
> **`/addChannel`**  
> `Add Channel`  
> `POST {"title": Channel Title, "description": Channel Description}`  
> `Returns {"id": New Channel ID}`  

> **`/addMessage`**  
> `Add Message`  
> `POST {"id": Existing Channel ID, "title": Message Title, "description": Message Content}`  
> `Returns {"id": New Message ID}`  

> **`/modifyChannel`**  
> `Modify Channel Data`  
> `POST {"id": Existing Channel ID, ...kwargs}`  
> `All key-value pairs in kwargs will overwrite the corresponding key-value pairs of the channel`  
> `Returns 200 on success`  

> **`/modifyMessage`**  
> `Modify Message Data`  
> `POST {"channelId": Existing Channel ID, "messageId": Existing Message ID, ...kwargs}`  
> `All key-value pairs in kwargs will overwrite the corresponding key-value pairs of the message`  
> `Returns 200 on success`  
>  
> **`/deleteChannel`**  
> `Delete Channel`  
> `POST {"id": Existing Channel ID}`  
> `Returns 200 on success`  

> **`/deleteMessage`**  
> `Delete Message`  
> `POST {"channelId": Existing Channel ID, "messageId": Existing Message ID}`  
> `Returns 200 on success`  

> **`/getMessageList`**  
> `Get Message List`  
> `POST {"id": Existing Channel ID}`  
> `Returns JSON data of all messages in the corresponding channel`  

> **`/getChannelList`**  
> `Get Channel List`  
> `Direct Access`  
> `Returns JSON data of all channels (excluding item key-value pairs)`  