import re
import requests

if __name__ == '__main__':
    res = requests.get('http://192.168.99.18/zh_cn')
    print(res.text)
