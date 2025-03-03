import json
import pyperclip

SID = 3
GID = 3

read = input("请输入希望测试的序号，连续序号可以用-相连，中间空格分开：").split(" ")
l = []
for r in read:
    if "-" in r:
        a, b = r.split("-")
        l.extend(list(range(int(a), int(b) + 1)))
    else:
        l.append(int(r))

url = "https://tenhou.net/5/#json="
file_name = f"Final/S{SID}_G{GID}.json"
with open(file_name, 'r', encoding='utf-8') as file:
    json_data = json.load(file)
    game_list = json_data["log"]
    new_game_list = [] 
    for i in l:
        new_game_list.append(game_list[i])
    json_data["log"] = new_game_list
    url += json.dumps(json_data)
    
    pyperclip.copy(url)
    print("已复制第", l, "局到剪贴板")