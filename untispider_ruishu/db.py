

import redis
import config as settings
from better_exceptions.encoding import to_unicode, to_byte

__all__ = ["redis_db",]

class RedisDB:

    def __init__(self, **kwargs):
        try:
            self.__pool = redis.ConnectionPool(**kwargs)  # redis默认端口是6379
            self._redis = redis.Redis(connection_pool=self.__pool)
        except Exception as e:
            input('''
            ****************
                未链接到redis数据库，
                您当前的链接信息为：
                    host = {}
                    port = {}
                    db = {}
                    passwd = {}
                Exception: {}
            ******************
            '''.format(settings['REDIS_CONFIG']['host'], settings['REDIS_CONFIG']['port'],
                       settings['REDIS_CONFIG']['db'], settings['REDIS_CONFIG']['passwd'], str(e))
                  )

    # 集合操作
    def sadd(self, key, vals):
        '''
        @summary: 使用无序set集合存储数据， 去重
        ---------
        @param key:
        @param values: 值； 支持list 或 单个值
        ---------
        @result: 若库中存在 返回0，否则入库，返回1。 批量添加返回None
        '''

        if isinstance(vals, list):
            pipe = self._redis.pipeline(
                transaction=True)  # redis-py默认在执行每次请求都会创建（连接池申请连接）和断开（归还连接池）一次连接操作，如果想要在一次请求中指定多个命令，则可以使用pipline实现一次请求指定多个命令，并且默认情况下一次pipline 是原子性操作。
            pipe.multi()
            for value in vals:
                pipe.sadd(key, to_byte(value))
            pipe.execute()
        else:
            return self._redis.sadd(key, vals)

    def sget(self, key, count=1, is_pop=False):
        '''
        返回 list 如 ['1'] 或 []
        @param key:
        @param count:
        @param is_pop:
        @return:
        '''
        datas = []
        if is_pop:
            count = count if count <= self.sget_count(key) else self.sget_count(key)
            if count:
                if count > 1:
                    pipe = self._redis.pipeline(transaction=True)  # redis-py默认在执行每次请求都会创建（连接池申请连接）和断开（归还连接池）一次连接操作，如果想要在一次请求中指定多个命令，则可以使用pipline实现一次请求指定多个命令，并且默认情况下一次pipline 是原子性操作。
                    pipe.multi()
                    while count:
                        pipe.spop(key)
                        count -= 1
                    datas = pipe.execute()

                else:
                    datas.append(self._redis.spop(key))

        else:
            datas = self._redis.srandmember(key, count)

        return [to_unicode(val) for val in datas]
    
    def sget_count(self, key):
        return self._redis.scard(key)
    
    # 连接池自动关闭连接
    def close(self):
        pass

redis_db = RedisDB(**settings.REDIS_CONFIG)

if __name__ == '__main__':
    db = RedisDB(**settings.REDIS_CONFIG)
    for val in db.sget('gov:detail_content', 1):
        print(val)