
__author__ = 'Silva'

'''
mitproxy 消息拦截 js注入
抓取国家药监局等严重瑞数加密相关站点信息
详情页消息暂存redis
'''

# 内置模块
import re
# 第三方模块
import mitmproxy
from mitmproxy import ctx
from urllib.parse import urljoin
from scrapy.selector import Selector
# 本地模块
from db import redis_db, RedisDB,to_unicode

start_key = 'gov:start_task'
catlog_key = 'gov:catlog_task'
detail_key = 'gov:detail_task'
content_key = 'gov:detail_content'


class RuiShuCapture:

    def response(self, flow: mitmproxy.http.HTTPFlow):
        url = flow.request.url
        page_content_reload = ">>{tip}\n\r\t <script>setTimeout(function(){{window.location.reload();}},{sleep_time_msec});</script>"
        page_content_redirect = ">>{tip}\n\r\t <script>setTimeout(function(){{window.location.href='{url}';}},{sleep_time_msec});</script>"

        # 异常页面判断
        # pass

        if '://fgw.hubei.gov.cn/' in url:

            # 获取任务
            task_url = get_task()

            if not task_url:
                redirect_page_content = page_content_reload.format(tip='>> 队列任务已经消费完成', sleep_time_msec=10000)
            else:
                print('>'*10, task_url[0])
                tip = '加载当前任务链接: {}'.format(url)

                # 文本转成selector对象
                selector = Selector(text=flow.response.text)

                # 缓存当前满足的任务列表
                cach_task(url, flow.response.text, selector)

                # 详情页面数据处理
                deal_data(url, flow.response.text, selector)
                redirect_page_content = page_content_redirect.format(tip=tip, url=task_url[0], sleep_time_msec=1000)
        else:
            # '其他页面重定向延时加载'
            url = 'http://fgw.hubei.gov.cn/gzjj/tzgg/tz/201310/t20131029_1012002.shtml'
            redirect_page_content = page_content_redirect.format(tip='非资源页面重定向', url=url, sleep_time_msec=3000)
        # 页面重定向
        if redirect_page_content:
            flow.response.set_text(redirect_page_content + flow.response.text)

def get_task():
    '''
    获取任务
    :return:
    '''
    # 第一优先从catlog任务获取
    task_url = redis_db.sget(start_key, count=1,is_pop=True)
    # 第二优先从pages任务获取
    if not task_url:
        task_url = redis_db.sget(catlog_key, count=1, is_pop=True)
    # 最后从detail任务获取
    if not task_url:
        task_url = redis_db.sget(detail_key, count=1, is_pop=True)
    return task_url

def cach_task(url, text, selector):
    '''
    缓存任务
    :return:
    '''
    # 分页任务缓存
    page_count = re.findall(r"createPageHTML\((\d+)", text, re.S)
    if page_count and 'index_' not in url:
        url_list = []
        for page in range(1, int(page_count[0])):
            url_list.append(urljoin(url, 'index_{}.shtml'.format(page)))
        redis_db.sadd(catlog_key, url_list)
        ctx.log('缓存 catlog_page_list 成功!')

    # 详情任务缓存
    detail_url_list = selector.css('.lsj-list li a::attr(href)').extract()
    if detail_url_list:
        redis_db.sadd(detail_key, detail_url_list)
        ctx.log('缓存 detail_url_list 成功!')

def deal_data(url, text, selector):
    '''
    处理响应结果
    :return:
    '''
    if 'ArticleTitle' in text and 't20131029_1012002' not in url:
        redis_db.sadd(content_key, text)
        ctx.log('详情内容获取成功, 已缓存至redis!')


addons = [
    RuiShuCapture(),
]