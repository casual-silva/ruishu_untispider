
# -*- coding: utf-8 -*-
'''
Created on 2019/5/18 9:52 PM
---------
@summary:
---------
@author:
'''
from mit_proxy_capture import RuiShuCapture
from mitmproxy import options
from mitmproxy import proxy
from mitmproxy.tools.dump import DumpMaster
from db import redis_db

def start():
    ip = '127.0.0.1'
    port = 8080
    print("温馨提示：服务IP {} 端口 {} 请确保代理已配置".format(ip, port))

    myaddon = RuiShuCapture()
    opts = options.Options(listen_port=port)
    pconf = proxy.config.ProxyConfig(opts)
    m = DumpMaster(opts)
    m.server = proxy.server.ProxyServer(pconf)
    m.addons.add(myaddon)

    try:
        m.run()
    except KeyboardInterrupt:
        m.shutdown()


if __name__ == '__main__':
    tart_url = [
        'http://fgw.hubei.gov.cn/gzjj/tzgg/tz/',
        'http://fgw.hubei.gov.cn/gzjj/dtyw/fgyw/',

    ]
    # redis_db.sadd('gov:start_task', tart_url)
    if not redis_db.sget('gov:start_task'):
        # redis_db.sadd('gov:start_task', tart_url)
        print('not fund start_task !')
    else:
        start()
