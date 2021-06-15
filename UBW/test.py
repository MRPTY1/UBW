import re
import requests

if __name__ == '__main__':
    res = requests.get('https://adguard.com/zh_cn/welcome.html')
    print(res.text)
