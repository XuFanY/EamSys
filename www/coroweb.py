#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'XFanYu'
__email__ = 'Xfanyu@outlook.com'
import asyncio
import inspect
import logging
import os
from aiohttp import web
from functools import wraps
from urllib import parse


class APIError(Exception):
    """
    the base APIError which contains error(required), data(optional) and message(optional).
    """
    def __init__(self, error, data='', message=''):
        super(APIError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message


# Define decorator @request('/path')
# request(str){'GET','POST'}
def gp(path, request):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = request
        wrapper.__route__ = path
        return wrapper
    return decorator


# 获取函数func的参数信息
def get_args(func):
    has_kw_args, has_var_kw_args = False, False
    kw_args, non_dft_kw_args = [], []
    params = inspect.signature(func).parameters
    for name, param in params.items():
        if not has_var_kw_args and param.kind == inspect.Parameter.VAR_KEYWORD:
            has_var_kw_args = True
            continue
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            kw_args.append(name)
            if param.default == inspect.Parameter.empty:
                non_dft_kw_args.append(name)
    if len(kw_args) > 0:
        has_kw_args = True
    return tuple(kw_args), tuple(non_dft_kw_args), has_kw_args, has_var_kw_args


# 从URL函数中分析需要接受的参数
class RequestHandler(object):
    # func->function name
    def __init__(self, app, func):
        self._app = app
        self._func = func
        self._kw_args, self._non_dft_kw_args, self._has_kw_args, self._has_var_kw_args = get_args(func)
        # self._has_request_arg = has_request_arg(func)

    async def __call__(self, request):
        kw = None
        if self._has_var_kw_args or self._has_kw_args or self._non_dft_kw_args:
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadRequest('Missing Content-Type.')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    params = await request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest('JSON body must be object.')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest('Unsupported Content-Type: %s' % request.content_type)
            if request.method == 'GET':
                qs = request.query_string
                if qs:
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
        else:
            if not self._has_var_kw_args and self._kw_args:
                # remove all unnamed kw:
                copy = dict()
                for name in self._kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            # check named arg:
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warning('Duplicate arg name in named arg and kw args: %s' % k)
                kw[k] = v
        # if self._has_request_arg:
        #     kw['request'] = request
        # check required kw:
        if self._non_dft_kw_args:
            for name in self._non_dft_kw_args:
                if name not in kw:
                    return web.HTTPBadRequest('Missing argument: %s' % name)
        logging.info('call with args: %s' % str(kw))
        try:
            r = await self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)


# 将module中的URL函数注册到app中
def add_routes(app, module):
    n = module.rfind('.')
    if n == (-1):
        mod = __import__(module, globals(), locals())
    else:
        name = module[n + 1:]
        mod = getattr(__import__(module[:n], globals(), locals(), [name]), name)
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        func = getattr(mod, attr)
        if callable(func):
            method = getattr(func, '__method__', None)
            path = getattr(func, '__route__', None)
            # 注册URL
            if method and path:
                if not asyncio.iscoroutinefunction(func) and not inspect.isgeneratorfunction(func):
                    func = asyncio.coroutine(func)
                logging.info('Add route %s %s => %s(%s)' %
                             (method, path, func.__name__, ', '.join(inspect.signature(func).parameters.keys())))
                app.router.add_route(method, path, RequestHandler(app, func))


# 给app添加静态文件的路径
def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    logging.info('Add static %s => %s' % ('/static/', path))


# 判断函数func是否有'request'参数
# def has_request_arg(func):
#     sig = inspect.signature(func)
#     params = sig.parameters
#     found = False
#     for name, param in params.items():
#         if name == 'request':
#             found = True
#             continue
#         if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and
#                       param.kind != inspect.Parameter.KEYWORD_ONLY and
#                       param.kind != inspect.Parameter.VAR_KEYWORD):
#             raise ValueError('`request` parameter must be the last named parameter in function: %s%s' %
#                              (func.__name__, str(sig)))
#     return found