import json
import pyperclip
import webbrowser
import getopt
import sys

SID = 3
GID = 9

traversal = False

opts, args = getopt.getopt(sys.argv[1:], "s:g:", ["traversal", "empty"])
for opt, arg in opts:
    if opt == "-s":
        SID = int(arg)
    elif opt == "-g":
        GID = int(arg)
    elif opt == "--traversal":
        traversal = True

l = []

if not traversal:
    read = input("请输入希望测试的序号，连续序号可以用-相连，中间空格分开：").split(" ")
    for r in read:
        if "-" in r:
            a, b = r.split("-")
            l.extend(list(range(int(a), int(b) + 1)))
        else:
            l.append(int(r))


url = "https://tenhou.net/6/#json="
for opt, _ in opts:
    if opt == "--empty": url = ""
    
file_name = f"Final/S{SID}_G{GID}.json"
with open(file_name, 'r', encoding='utf-8') as file:
    json_data = json.load(file)
    game_list = json_data["log"]
    new_game_list = [] 

    for i in l:
        new_game_list.append(game_list[i])
    if traversal:
        new_game_list = game_list

    json_data["log"] = new_game_list
    url += json.dumps(json_data)
    
    pyperclip.copy(url)
    print("已复制第", l, "局到剪贴板")

    if traversal:
        _new = 1
        for game in new_game_list:
            json_data["log"] = [game]
            myurl = "https://tenhou.net/6/#json=" + json.dumps(json_data) 
            webbrowser.open(myurl, new=_new)
            _new = 2