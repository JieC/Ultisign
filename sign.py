#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import requests
import re
import json
import logging
import codecs
import sys


logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('sign.log', 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Sign:
    def __init__(self, config, site):
        self.session = requests.Session()
        self.session.headers.update(
            {'user-agent': 'Mozilla/5.0 (Linux; \
            Android 5.1.1; Nexus 4 Build/LMY48T) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/40.0.2214.89 Mobile Safari/537.36'})
        self.login = config['login']
        self.base_url = config['base_url']
        self.login_page = config['login_page']
        self.login_extractor = config['login_extractor']
        self.extractor_key = config['extractor_key']
        self.login_url = config['login_url']
        self.login_success = config['login_success']
        self.sign_page = config['sign_page']
        self.sign_extractor = config['sign_extractor']
        self.sign_url = config['sign_url']
        self.sign_success = config['sign_success']
        self.site = site

    def do_login(self):
        extract = ''
        if self.login_page[0]:
            for l in self.login_page:
                login_page_r = self.session.get(self.base_url + l)
                if self.login_extractor:
                    login_extract = re.search(
                        self.login_extractor,
                        login_page_r.text)
                    if login_extract:
                        extract = login_extract.group(1)
                        if self.extractor_key:
                            self.login[self.extractor_key] = extract
                    else:
                        logger.error('Not able to find login extract')
                        return
        login = self.session.post(
            self.base_url + self.login_url.format(extract=extract),
            data=self.login)
        if self.login_success[0] in getattr(login, self.login_success[1]):
            if self.sign_url:
                self.do_sign()
            else:
                logger.info(self.site + ':Login Successful')
        else:
            logger.error('Login Failed')
            logger.debug(login.text)

    def do_sign(self):
        extract = ''
        if self.sign_page:
            sign_page_r = self.session.get(self.base_url + self.sign_page)
            if self.sign_extractor:
                sign_extract = re.search(self.sign_extractor, sign_page_r.text)
                if sign_extract:
                    extract = sign_extract.group(1)
                else:
                    logger.error('Not able to find sign extract')
                    return

        sign = self.session.get(
            self.base_url + self.sign_url.format(extract=extract))
        if logger.isEnabledFor(logging.DEBUG):
            is_json = re.search(
                'json|javascript', sign.headers['Content-Type'])
            if is_json:
                logger.debug(codecs.getdecoder('unicode-escape')(sign.text)[0])
            else:
                logger.debug(sign.text)
        if self.sign_success[0] in getattr(sign, self.sign_success[1]):
            logger.info(self.site + ':Sign Successful')
        else:
            logger.error('Sign Failed')
            logger.debug(sign.text)


def main():
    with codecs.open('sign.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    for site in config['active']:
        s = Sign(config[site], site)
        s.do_login()

if __name__ == "__main__":
    if '-d' in sys.argv:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    main()
