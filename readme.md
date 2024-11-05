# 基于RSS订阅的消息分发服务

[English version](readme-en.md)

## 想法来源：  
&emsp;&emsp;最近在维护博客服务器， 在服务器宕机或者出现其他问题时，需要及时将消息推送给各个管理员，以便快速解决问题。起初尝试了微信，飞书等私有平台，但要么api较为复杂，要么根本不提供接口，之后又尝试了电子邮件， 但邮件大概率会被丢到垃圾箱，或是无法及时地被推送到手机上。这时我想起了RSS订阅，一个现在已不太流行的信息聚合协议，其基于xml，易于生成和管理，且具有平台无关性，任何平台上只需要RSS阅读器就可以订阅和获取消息推送，因此有了这个项目

## rssServer.py：  
&emsp;&emsp;基于Flask实现的RSS源，提供HTTP api以实现频道、消息的增减修改操作  
## xmlgenerator.py:  
&emsp;&emsp;将储存在json文件中的频道和消息转换为xml文件，提供给RSS阅读器
  
HTTP根路径 "/" 是提供给RSS的xml文件  
填入RSS阅读器的feed链接中即可订阅  
  
## HTTP api:  
> **`/addChannel`**  
> `添加频道`  
> `POST {"title": 频道标题, "description": 频道描述}`  
> `返回 {"id": 新频道的id}`  
>   
> **`/addMessage`**  
> `添加消息`  
> `POST {"id": 存在的频道id, "title": 消息标题, "description": 消息内容}`  
> `返回 {"id": 新消息的id}`  
>   
> **`/modifyChannel`**  
> `修改频道数据`  
> `POST {"id": 存在的频道id, ...kwargs}`  
> `kwargs中的所有键值对将覆盖对应频道的键值对`  
> `成功则返回200`  
>   
> **`/modifyMessage`**  
> `修改消息数据`  
> `POST {"channelId": 存在的频道id, "messageId": 存在的消息id, ...kwargs}`  
> `kwargs中的所有键值对将覆盖对应消息的键值对`  
> `成功则返回200`  
>   
> **`/deleteChannel`**  
> `删除频道`  
> `POST {"id": 存在的频道id}`  
> `成功则返回200`  
>   
> **`/deleteMessage`**  
> `删除消息`  
> `POST {"channelId": 存在的频道id, "messageId": 存在的消息id}`  
> `成功则返回200`  
>   
> **`/getMessageList`**  
> `获取消息列表`  
> `POST {"id": 存在的频道id}`  
> `返回对应频道下所有消息的json`  
>   
> **`/getChannelList`**  
> `获取频道列表`  
> `直接访问`  
> `返回所有频道的json（除了item键值对）`  