#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'XFanYu'
__email__ = 'Xfanyu@outlook.com'
'''
async web application.
'''
import asyncio
import json
import logging
import os
from aiohttp import web
from coroweb import add_routes, add_static
from jinja2 import Environment, FileSystemLoader

import orm
from configuration import configs


# 记录URL日志的logger中间件
@web.middleware
async def logger(request, handler):
    # 记录日志
    logging.info('Request: %s %s' % (request.method, request.path))
    # 继续处理请求
    response = await handler(request)
    return response


async def response_factory(app, handler):
    # 将返回值转换为web.Response对象后返回
    async def response(request):
        logging.info('Response handler...')
        rst = await handler(request)
        if isinstance(rst, web.StreamResponse):
            return rst
        if isinstance(rst, bytes):
            resp = web.Response(body=rst)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(rst, str):
            if rst.startswith('redirect:'):
                return web.HTTPFound(rst[9:])
            resp = web.Response(body=rst.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(rst, dict):
            template = rst.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(rst, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                resp = web.Response(body=app['__templating__'].get_template(template).render(**rst).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(rst, int) and 100 <= rst < 600:
            return web.Response(body=rst)
        if isinstance(rst, tuple) and len(rst) == 2:
            t, m = rst
            if isinstance(t, int) and 100 <= t < 600:
                return web.Response(t, str(m))
        # default:
        resp = web.Response(body=str(rst).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp
    return response


# 设置app的html文件的路径以及在html文件使用后端变量的格式
def init_jinja2(app):
    options = {'autoescape': True, 'auto_reload': True,
               'block_start_string': '{%', 'block_end_string': '%}',
               'variable_start_string': '{{', 'variable_end_string': '}}'}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('Set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    app['__templating__'] = env
    logging.info('Init jinja2 finish')


# 初始化app运行环境(创建数据库连接池、添加网页get/post请求的处理函数等)
async def init(loop):
    database = configs['database']
    await orm.create_pool(loop=loop, host=database['host'], port=database['port'],
                          user=database['user'], password=database['password'], db=database['db'])
    app = web.Application(middlewares=[logger, response_factory])
    init_jinja2(app)
    add_routes(app, 'handlers')

    add_static(app)
    srv = await loop.create_server(app._make_handler(), database['host'], 9000)
    logging.info('Server started at http://%s:9000...' % database['host'])
    return srv


# 主函数入口
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()
