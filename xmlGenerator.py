"""
{"channels":
    [
        {
            "title":"Channel title",
            "link":"",
            "description":"Channel description",
            "items":
                [
                    {
                        "title":"Item title",
                        "link":"Item link",
                        "description":"Item description"
                    }
                ]
        }
    ]
}
"""
from json import loads


def addList(elementsList: list, lines: list, indent: int, listName: str):
    for element in elementsList:
        lines.append(indent * "   " + "<" + listName + ">\n")
        addDict(element, lines, indent + 1)
        lines.append(indent * "   " + "</" + listName + ">\n")


def addDict(elementsDict: dict, lines: list, indent: int):
    for element in elementsDict.items():
        if isinstance(element[1], list):
            addList(element[1], lines, indent, element[0])
        elif isinstance(element[1], str):
            lines.append(indent * "   " + "<" + element[0] + ">" + element[1] + "</" + element[0] + ">\n")
        else:
            lines.append(indent * "   " + "<" + element[0] + ">" + str(element[1]) + "</" + element[0] + ">\n")


def genXML():
    with open("rss.json", mode='r') as JsonFile:
        rss = loads(JsonFile.readline())

    with open("rss.xml", mode='w') as xmlFile:
        lines = ["<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n", "<rss version=\"2.0\">\n"]
        addDict(rss, lines, 1)
        lines.append("</rss>\n")
        xmlFile.writelines(lines)
