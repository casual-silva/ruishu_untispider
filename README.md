### 
mitproxy 消息拦截 抓取国家药监局等严重瑞数加密相关站点信息

![image.png](https://upload-images.jianshu.io/upload_images/13378161-0b7e934af2eb4e6b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)



### 简单架构流程

队列服务：Redis

一.  Main 主程序入口  > 推送起始任务 > mitproxy 消息拦截

二. 核心处理流程 

1.  任务获取 redis: get_task_url

2. 消息处理： 判断页面生成并缓存新的任务列表 > redis

   ​					过滤无效页面

   ​					···

3. 数据处理：最终资源页面处理 > 解析保存至数据库 or 暂存至redis

4. 消息返回  response 注入js 使页面重定向至新任务

     

   任务循环直至redis任务消费完