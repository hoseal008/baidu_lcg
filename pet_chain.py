# -*- coding:utf-8 -*-
import ConfigParser
import json
import random
import time
import base64

import requests

from client import online_ocr


class PetChain():
    def __init__(self):
        self.degree_map = {
            0: "common",
            1: "rare",
            2: "excellence",
            3: "epic",
            4: "mythical",
        }
        self.degree_conf = {}
        self.interval = 1

        self.cookies = ''
        self.username = ''
        self.password = ''
        self.headers = {}
        self.get_headers()
        self.get_config()

    def get_config(self):
        config = ConfigParser.ConfigParser()
        config.read("config.ini")

        for i in range(5):
            try:
                amount = config.getfloat("Pet-Chain", self.degree_map.get(i))
            except Exception, e:
                amount = 100
            self.degree_conf[i] = amount

        self.interval = config.getfloat("Pet-Chain", "interval")


    def get_headers(self):
        with open("data/headers.txt") as f:
            lines = f.readlines()
            for line in lines:
                splited = line.strip().split(":")
                key = splited[0].strip()
                value = ":".join(splited[1:]).strip()
                self.headers[key] = value

    def get_market(self):
        try:
            data = {
                "appId": 1,
                "lastAmount": None,
                "lastRareDegree": None,
                "pageNo": 1,
                "pageSize": 10,
                "petIds": [],
                # "querySortType": "AMOUNT_DESC",
                "querySortType": "AMOUNT_ASC",
                "requestId": 1517968317687,
                "tpl": "",
            }
            page = requests.post("https://pet-chain.baidu.com/data/market/queryPetsOnSale", headers=self.headers,
                                 data=json.dumps(data))
            if page.json().get(u"errorMsg") == u"success":
                # print "[->] purchase"
                # print ".",
                pets = page.json().get(u"data").get("petsOnSale")
                for pet in pets:
                    self.purchase(pet)
        except Exception, e:
            # print 'x',
            pass

    def purchase(self, pet):
        try:
            pet_id = pet.get(u"petId")
            pet_amount = pet.get(u"amount")
            pet_degree = pet.get(u"rareDegree")
            pet_validCode = pet.get(u"validCode")

            data = {
                "appId": 1,
                "petId": pet_id,
                "captcha": "",
                "seed": 0,
                "requestId": int(time.time() * 1000),
                "tpl": "",
                "amount": "{}".format(pet_amount),
                "validCode": pet_validCode
            }
            if float(pet_amount) <= self.degree_conf.get(pet_degree):


                querypet_data = {
                    "appId": 1,
                    "petId": pet_id,
                    "requestId": int(time.time() * 1000),
                    "tpl": ""
                }

                page = requests.post("https://pet-chain.baidu.com/data/pet/queryPetById", headers=self.headers,
                                     data=querypet_data)

                captcha, seed = self.get_captcha()
                assert captcha and seed, ValueError("验证码为空")

                jump_data = {
                    "appId": 1,
                    "requestId": int(time.time() * 1000),
                    "tpl": ""
                }

                page = requests.post("https://pet-chain.baidu.com/data/market/shouldJump2JianDan", headers=self.headers,
                                     data=json.dumps(jump_data), timeout=2)

                data['captcha'] = captcha
                data['seed'] = seed
                self.headers['Referer'] = "https://pet-chain.baidu.com/chain/detail?channel=market&petId={}&appId=1&validCode={}".format(pet_id, pet_validCode)
                page = requests.post("https://pet-chain.baidu.com/data/txn/create", headers=self.headers,
                                     data=json.dumps(data), timeout=2)
                resp = page.json()
                if resp.get(u"errorMsg") != u"验证码错误":
                    # cv2.imwrite("data/captcha_dataset/%s.jpg" % captcha, image)
                    print "Get one captcha sample"
                else:
                    # cv2.imwrite("data/captcha_dataset/neg_sample/%s.jpg" % str(time.time()).replace('.', '_'), image)
                    print "Get one negative sample"
                print json.dumps(resp, ensure_ascii=False)
        except Exception, e:
            print e

    def get_captcha(self):
        seed = -1
        captcha = -1
        try:
            data = {
                "requestId": int(time.time() * 1000),
                "appId": 1,
                "tpl": ""
            }
            page = requests.post("https://pet-chain.baidu.com/data/captcha/gen", data=json.dumps(data),
                                 headers=self.headers)
            resp = page.json()
            if resp.get(u"errorMsg") == u"success":
                seed = resp.get(u"data").get(u"seed")
                img = resp.get(u"data").get(u"img")
                captcha = online_ocr(img)
                if captcha == '####':
                    print "token error"
                    exit()
                # with open('ocr_result/%s.jpg' % captcha, 'wb') as f:
                #     f.write(base64.b64decode(img))
                print "\nCaptcha code: %s" % captcha
        except Exception, e:
            print e
        return captcha, seed

    def format_cookie(self, cookies):
        self.cookies = ''
        for cookie in cookies:
            self.cookies += cookie.get(u"name") + u"=" + cookie.get(u"value") + ";"
        self.headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Cookie': self.cookies,
            'Host': 'pet-chain.baidu.com',
            'Origin': 'https://pet-chain.baidu.com',
            'Referer': 'https://pet-chain.baidu.com/chain/dogMarket?t=1517829948427',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
        }

        with open("data/headers.txt", "w") as f:
            for key, value in self.headers.items():
                f.write("{}:{}\n".format(key, value))

    def run(self):
        while True:
            pc.get_market()
            time.sleep(float(random.randint(1, 10))/10.0)
            # time.sleep(self.interval)


if __name__ == "__main__":
    pc = PetChain()
    pc.run()
