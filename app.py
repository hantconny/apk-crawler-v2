# -*- coding:utf-8 -*-
import time
import traceback

from DrissionPage import ChromiumPage
from loguru import logger

driver = ChromiumPage()

logger.add('apk_crawler_{time:YYYYMMDD}.log', rotation="50 MB", retention="3 days",
           compression="gz", enqueue=True)


def flush_data(file, data):
    with open(file, mode='w', encoding='utf-8') as file:
        file.write('\n'.join(['#@=|||=@#'.join([app, dev, cat, down, desc, '', '']) for app, dev, cat, down, desc in set(data)]))


def google_play(box, _category):
    app_name = box.ele('.grid-item-title').text
    app_developer = box.ele('.grid-item-developer').text
    app_category = _category
    package_name = box.ele('.grid-item-title').attr('href').rsplit('/', 1)[-1]

    tab = driver.new_tab()
    try:
        tab.get("https://play.google.com/store/apps/details?id={}".format(package_name))

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
        desc = ''
    finally:
        tab.close()

    logger.info('#@=|||=@#'.join([app_name, app_developer, app_category, downloads, desc, '', '']))

    return app_name, app_developer, app_category, downloads, desc


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


def category():
    driver.get('https://apkpure.com/app')

    # 网站的样式就包含空格，不要去掉
    return [i_category.attr('href') for i_category in driver.ele('.apk-name-list ').eles('tag:a')]


if __name__ == '__main__':
    result = []
    categories = category()
    # categories = ['https://apkpure.com/maps_and_navigation']
    for category_url in categories:
        category_title = category_url.rsplit('/', 1)[-1].replace('_', ' ').title().replace('And', '&')
        category_result = go(category_url, category_title)

        flush_data('{}.text'.format(category_title), category_result)

        result.extend(category_result)

    flush_data('app_info.text', result)
