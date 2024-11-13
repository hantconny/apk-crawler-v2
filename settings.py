import os.path
import time

"""
命名规则为/home/rhino/{project}/{sub-proj}
project可选值为: ip, sns, tor, stratum, apk
sub-proj可选值为: 
  ip: v4, v6
  sns: fb, tw, ut, ins, tk, vk
  tor: 直接存放
  stratum: 直接存放
  apk: 按日期存放
"""
DUMP_DIR = '/home/rhino/apk/{}'.format(time.strftime('%Y%m%d', time.localtime()))
if not os.path.exists(DUMP_DIR):
    os.makedirs(DUMP_DIR)

# Chrome 测试版解压位置，不要与客户机使用相同的 Chrome
CHROME_TEST = 'D:/ENV/chromedriver/chrome-win64/chrome.exe'

# 使用了 Drission，代理信息由系统代理控制，脚本不再控制代理

# https://apkpure.com/game 和 https://apkpure.com/app 两个大栏目
APKPURE_PATTERN = 'https://apkpure.com/{}'

# id 为包名
GOOGLE_PLAY_DETAIL_PAGE = 'https://play.google.com/store/apps/details?id={}'