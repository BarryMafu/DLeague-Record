import requests

# 目标 URL
url = "https://github.com/ShiningCrevice/DLeague-Data/blob/master/statistics/S3.csv"

try:
    # 发送 GET 请求获取内容
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功

    # 将内容保存到 test.txt 文件
    with open("test.txt", "w", encoding="utf-8") as file:
        file.write(response.text)

    print("内容已成功保存到 test.txt")
except requests.exceptions.RequestException as e:
    # 处理请求异常
    print(f"请求失败: {e}")
except Exception as e:
    # 处理其他异常
    print(f"发生错误: {e}")