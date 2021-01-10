import os
import sys
import time
import configparser

import argparse

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from metrics import JenkinsCollector

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Jenkins 登陆信息")
    parser.add_argument("--url", action='store', dest="url", required=True, help="Jenkins URL")
    parser.add_argument("--user", action='store', dest="user", required=True, help="Jenkins 用户名")
    parser.add_argument("--password", action='store', dest="password", required=True, help="Jenkins 密码")
    parsers = parser.parse_args()    

    collector = JenkinsCollector(url = parsers.url, username = parsers.user, password = parsers.password)
    REGISTRY.register(collector)
    print("jenkins-exporter 开始在端口 8888 上运行....")
    start_http_server(8888)
    while True:
        time.sleep(1)
