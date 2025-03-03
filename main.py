import convert 
import merge
import requests
import pyperclip

# TODO: SID and GID here
SID = 3
GID = 3

def open_browser():
    file_name = f"Final/S{SID}_G{GID}.json"
    url = "https://tenhou.net/5/#json="
    with open(file_name, 'r', encoding='utf-8') as file:
        url += file.read()

    response = requests.get(url)

    if response.status_code != 200:
        print("无法打开网页，错误码:", response.status_code)
        return
    
    with open(f"HTMLs/DLeague-S{SID}G{GID}.html", 'w', encoding='utf-8') as file:
        file.write(response.text)
    print("网页已保存到 DLeague-S{SID}G{GID}.html")

if __name__ == '__main__':
    from colorama import Fore
    print(Fore.YELLOW + "==============开始转换 Convert==============" + Fore.RESET)
    convert.convert(SID, GID)
    print(Fore.YELLOW + "===============开始合并 Merge===============" + Fore.RESET)
    merge.merge(SID, GID)
    print(Fore.GREEN +  "================完成 Complete===============" + Fore.RESET)

    # open_browser()
    file_name = f"Final/S{SID}_G{GID}.json"
    # Remove all the "/n" in the file
    with open(file_name, 'r', encoding='utf-8') as file:
        data = file.read()
        data = data.replace("\n", "")
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(data)

    url = "https://tenhou.net/5/#json="
    url += data 
    
    json_file_name = f"Json/S{SID}_G{GID}.json"
    with open(json_file_name, 'r', encoding='utf-8') as file:
        data = file.read()
        data = data.replace("\n", "")
    with open(json_file_name, 'w', encoding='utf-8') as file:
        file.write(data)

    print(f"最终合成结果已经去除换行保存到 {file_name}")
    print(f"分数表和操作表结果已经去除换行保存到 {json_file_name}")
    print("tenhou 网址已经复制到剪贴板")

    pyperclip.copy(url)


