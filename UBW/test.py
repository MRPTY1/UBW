import requests

if __name__ == '__main__':
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/88.0.4324.104 Safari/537.36',
               'content-type': 'application/x-www-form-urlencoded'
               }
    data = {
        'username': 'wangweirong@cloudtranslation.com',
        'password': 'yunyi666',
        'saveme': '1'
    }
    res = requests.post(url='https://www.ftchinese.com/users/login', headers=headers,
                        proxies={'https': '127.0.0.1:10809'}, data=data)
    print(res.headers)
    print(res.text)
