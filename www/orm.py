#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'XFanYu'
'''
interfaces for database operation
'''
import aiomysql
import logging


# 创建全局连接池pool,user、password和db是必须参数
async def create_pool(loop, **kw):
    db = kw['db']
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=db,
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )
    logging.info('create database %s connection pool successful!' % db)


# select语句封装函数
async def select(sql, args, size=None):
    logging.info('Execute MySQL statement: %s' % sql)
    async with __pool.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace('?', '%s'), args or ())
            if size:
                rst = await cur.fetchmany(size)
            else:
                rst = await cur.fetchall()
        logging.info('%d rows returned' % len(rst))
        return rst


# insert、update和delete语句的通用执行函数
async def execute(sql, args, autocommit=True):
    logging.info('Execute MySQL statement: %s' % sql)
    # print(args)
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                rows = cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        logging.info('%d rows affected' % rows)
        return rows


class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        # 排除类Model本身
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        # 获取表名table
        table = attrs['__table__']
        logging.info('found model: %s (table: %s)' % (name, table))
        # 获取所有的字段名fields(除主键)和主键名pk
        mappings = dict()
        fields, pks = [], []
        pk, pk_ud = None, None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('  found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                # 找到主键:
                if v.pk:
                    pks.append(k)
                    if pk:
                        pk += '`, `%s' % k
                        pk_ud += '`=? and `%s' % k
                    else:
                        pk = k
                        pk_ud = k
                else:
                    fields.append(k)
        if not pk:
            raise RuntimeError('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)
        attrs['__mappings__'] = mappings  # 保存属性和列的映射关系
        attrs['__pk__'] = pk  # 主键属性名
        attrs['__pks__'] = pks  # 多个主键属性名
        attrs['__fields__'] = fields  # 除主键外的属性名
        # 构造默认的select,insert,update和delete语句
        lbd_fields = list(map(lambda f: '`%s`' % f, fields))
        args, fields_str = '?' + ', ?' * (len(lbd_fields) + len(pks) - 1), ', '.join(lbd_fields)
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (pk, fields_str, table)
        attrs['__insert__'] = 'insert into `%s` (`%s`, %s) values (%s)' % (table, pk, fields_str, args)
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' \
                              % (table, ', '.join(map(lambda f: '`%s`=?' % f, fields)), pk_ud)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (table, pk_ud)
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def get_value(self, key):
        return getattr(self, key, None)

    def get_value_or_default(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default
                logging.debug('Using default value for %s: %s' % (key, value))
                setattr(self, key, value)
        return value

    @classmethod
    async def find_all(cls, where=None, args=None, **kw):
        # find objects by where clause.
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        order_by = kw.get('orderBy', None)
        if order_by:
            sql.append('order by')
            sql.append(order_by)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rst = await select(' '.join(sql), args)
        return [cls(**r) for r in rst]

    @classmethod
    async def find_by_fields(cls, fields, where=None, args=None):
        # find number by selected fields and where.
        sql = ['select %s _num_ from `%s`' % (fields, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rst = await select(' '.join(sql), args, 1)
        if len(rst) == 0:
            return None
        return rst[0]['_num_']

    @classmethod
    async def find_by_pk(cls, pk):
        # find object by primary key.
        rst = await select('%s where `%s`=?' % (cls.__select__, cls.__pk__), [pk], 1)
        if len(rst) == 0:
            return None
        return cls(**rst[0])

    async def save(self):
        pks = self.__pks__
        if len(pks) > 1:
            args = list(map(self.get_value, pks)) + list(map(self.get_value_or_default, self.__fields__))
        else:
            args = [self.get_value(self.__pk__)] + list(map(self.get_value_or_default, self.__fields__))
        # print(self.__insert__, args)
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warning('Failed to insert record: affected rows: %s' % rows)

    async def update(self):
        pks = self.__pks__
        if len(pks) > 1:
            args = list(map(self.get_value, self.__fields__)) + list(map(self.get_value, pks))
        else:
            args = list(map(self.get_value, self.__fields__)) + [self.get_value(self.__pk__)]
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warning('Failed to update by primary key: affected rows: %s' % rows)

    async def remove(self):
        args = [self.get_value(self.__pk__)]
        rows = await execute(self.__delete__, args)
        if rows != 1:
            logging.warning('Failed to delete by primary key: affected rows: %s' % rows)


# 字段基类
class Field(object):
    # field_type->字段类型,pk->字段是否为主键,default->字段的默认值
    def __init__(self, field_type, pk, default):
        self.field_type = field_type
        self.pk = pk
        self.default = default

    def __str__(self):
        return '<%s, %s>' % (self.__class__.__name__, self.field_type)


# varchar字段类
class Varchar(Field):
    def __init__(self, field_type='varchar(50)', pk=False, default=None):
        super().__init__(field_type, pk, default)


# bool字段类
class Bool(Field):
    def __init__(self, default=True):
        super().__init__('boolean', False, default)


# int/integer字段类
class Integer(Field):
    def __init__(self, pk=False, default=0):
        super().__init__('int', pk, default)


# real字段类
class Real(Field):
    def __init__(self, pk=False, default=0.0):
        super().__init__('real', pk, default)


# text字段类
class Text(Field):
    def __init__(self, default=None):
        super().__init__('text', False, default)
