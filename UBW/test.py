import re
import requests

if __name__ == '__main__':
    print(requests.get('https://www.baidu.com', proxies={'https': '159.75.19.163:10086'}).text)
