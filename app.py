# -*- coding:utf-8 -*-
import csv
import os.path
import time
import traceback

from DrissionPage import ChromiumPage, ChromiumOptions
from loguru import logger

from settings import CHROME_TEST, DUMP_DIR, GOOGLE_PLAY_DETAIL_PAGE, APKPURE_PATTERN

# 对于Chrome没有安装在默认位置的，指定Chrome安装路径。
if CHROME_TEST:
    ChromiumOptions().set_browser_path(CHROME_TEST).save()

driver = ChromiumPage()

logger.add(os.path.join(DUMP_DIR, 'apk_crawler_{time:YYYYMMDD}.log'),
           rotation="50 MB", retention="3 days",
           compression="gz", enqueue=True, encoding='utf-8')


def flush_data(filename, data):
    with open(os.path.join(DUMP_DIR, filename), mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerows([[app, dev, cat, desc, down, '', ''] for app, dev, cat, desc, down in set(data)])


def google_play(box, _category):
    app_name = box.ele('.grid-item-title').text
    app_developer = box.ele('.grid-item-developer').text
    app_category = _category
    package_name = box.ele('.grid-item-title').attr('href').rsplit('/', 1)[-1]

    tab = driver.new_tab()
    try:
        tab.get(GOOGLE_PLAY_DETAIL_PAGE.format(package_name))

        detail_btn = tab.ele('.VfPpkd-Bz112c-LgbsSe yHy1rc eT1oJ QDwDD mN1ivc VxpoF')
        if detail_btn:
            detail_btn.click()

            downloads = tab.eles('downloads')[-1].text.split(' ')[0]
            desc = " ".join(tab.ele('.fysCi').eles('tag:div')[0].text.splitlines())
        else:
            downloads = '0'
            desc = ''

    except Exception as e:
        logger.error(traceback.format_exc())
        downloads = '0'
        desc = 'None'
    finally:
        tab.close()

    logger.info('#@=|||=@#'.join([app_name, app_developer, app_category, desc, downloads]))

    return app_name, app_developer, app_category, desc, downloads


def keep_click(load_more_btn):
    if not load_more_btn:
        return False

    load_more_btn_style = load_more_btn.attr('style')
    if load_more_btn_style is None:
        return True

    if 'none' not in load_more_btn_style:
        return True

    return False


def go(url, category):
    try:
        driver.get(url)

        load_more_btn = driver.ele('.show-more')

        while keep_click(load_more_btn):
            driver.ele('.show-more').click()
            time.sleep(5)
            load_more_btn = driver.ele('.show-more')

        return [google_play(box, category) for box in driver.eles('.grid-text-box')]

    except Exception as e:
        print(traceback.format_exc())


def category(game_or_app):
    driver.get(APKPURE_PATTERN.format(game_or_app))

    # 网站的样式就包含空格，不要去掉
    return [i_category.attr('href') for i_category in driver.ele('.apk-name-list ').eles('tag:a')]


if __name__ == '__main__':
    result = []
    categories = category('game') + category('app')
    # categories = ['https://apkpure.com/art_and_design']
    for category_url in categories:
        category_title = category_url.rsplit('/', 1)[-1].replace('_', ' ').title().replace('And', '&')
        category_result = go(category_url, category_title)

        flush_data('{}.csv'.format(category_title), category_result)

        result.extend(category_result)

    flush_data('apk_info.csv', result)
