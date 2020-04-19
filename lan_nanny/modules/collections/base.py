"""Base Collection

"""
from datetime import timedelta

import arrow


class Base:

    def __init__(self, conn=None, cursor=None):
        """Base collection constructor. var `table_name must be the """
        self.conn = conn
        self.cursor = cursor

        self.table_name = None
        self.collect_model = None

    def get_by_ids(self, model_ids: list) -> list:
        """Get models instances by their ids from the database."""
        model_ids = list(set(model_ids))
        sql_ids = self.int_list_to_sql(model_ids)
        sql = """
            SELECT *
            FROM %(table_name)s
            WHERE id IN (%(ids)s); """ % {
        'table_name': self.table_name,
        'ids': sql_ids,
        }
        self.cursor.execute(sql)
        raws = self.cursor.fetchall()
        prestine = self.build_from_lists(raws)
        return prestine

    def get_paginated(self,
        limit: int=20,
        offset: int=0,
        order_by: dict={},
        where_and: list=[]) -> list:
        """
        Get paginated collection of models.
        :param limit: The limit of results per page.
        :param offset: The offset to return pages from or the "page" to return.
        :param order_by: A dict with the field to us, and the direction of the order.
            example value for order_by:
            {
                'field': 'last_seen',
                'op' : 'DESC'
            }
        :param where_and: a list of dictionaries, containing fields, values and the operator of AND
            statements to concatenate for the query.
            example value for where_and:
            [
                {
                    'field': 'last_seen',
                    'value': last_online,
                    'op': '>='
                }
            ]
        :returns: A list of model objects, hydrated to the default of the base.build_from_list()

        """
        sql_vars = {
            'table_name': self.table_name,
            'limit': limit,
            'offset': offset,
            'where': self._get_pagination_where_and(where_and),
            'order': self._get_pagination_order(order_by)
        }
        sql = """
            SELECT *
            FROM %(table_name)s
            %(where)s
            %(order)s
            LIMIT %(limit)s OFFSET %(offset)s;""" % sql_vars
        self.cursor.execute(sql)
        raw = self.cursor.fetchall()
        prestine = []
        for raw_item in raw:
            new_object = self.collect_model(self.conn, self.cursor)
            new_object.build_from_list(raw_item)
            prestine.append(new_object)
        return prestine

    def get_last(self) -> list:
        """Get last x created models descending."""
        sql = """
            SELECT *
            FROM %s
            ORDER BY created_ts DESC
            LIMIT 10;""" % self.table_name
        self.cursor.execute(sql)
        raw = self.cursor.fetchall()
        prestines = self.build_from_lists(raw)
        return prestines

    def get_pagination_info(self, base_url: str, page: int, per_page: int) -> dict:
        """
        Get pagination details, supplementary info from the get_paginated method. This contains
        details like total_units, next_page, previous page and other details needed for properly
        drawing pagination info on a GUI.

        """
        pagination = {}
        pagination['total_units'] = self.get_count_total()
        pagination['first_page'] = 1
        pagination['current_page'] = page
        pagination['last_page'] = self.get_total_pages(pagination['total_units'], per_page)
        pagination['next_page'] = self._get_next_page(page, pagination['last_page'])
        pagination['previous_page'] = self._get_previous_page(page)
        pagination['base_url'] = base_url
        pagination = self._get_urls(base_url, pagination)
        return pagination

    def get_count_total(self) -> int:
        """Get count of total model instances in table."""
        sql = """
            SELECT COUNT(*)
            FROM %s;
            """ % self.table_name

        self.cursor.execute(sql)
        raw_scans_count = self.cursor.fetchone()
        return raw_scans_count[0]

    def get_all(self) -> list:
        """
            Get all of a models instances from the database.
            @note: This should NOT be used unless a model has a VERY limited set of results.
            DEPRICATED!
        """
        sql = """
            SELECT *
            FROM %s;
            """ % self.table_name
        self.cursor.execute(sql)
        raws = self.cursor.fetchall()
        pretties = []
        for raw in raws:
            model = self.collect_model()
            model.build_from_list(raw)
            pretties.append(model)
        return pretties

    def get_count_since(self, seconds_since_created: int) -> int:
        """Get count of model instances in table created in last x seconds."""
        then = arrow.utcnow().datetime - timedelta(seconds=seconds_since_created)
        sql = """
            SELECT COUNT(*)
            FROM %s
            WHERE created_ts > "%s";
            """ % (self.table_name, then)
        self.cursor.execute(sql)
        raw_scans_count = self.cursor.fetchone()
        return raw_scans_count[0]

    def get_since(self, seconds_since_created: int) -> int:
        """Get model instances created in last x seconds."""
        then = arrow.utcnow().datetime - timedelta(seconds=seconds_since_created)
        sql = """
            SELECT *
            FROM %s
            WHERE created_ts > "%s"
            ORDER BY id DESC;
            """ % (self.table_name, then)
        self.cursor.execute(sql)
        raw = self.cursor.fetchall()
        prestines = []
        for raw_item in raw:
            new_object = self.collect_model(self.conn, self.cursor)
            new_object.build_from_list(raw_item)
            prestines.append(new_object)
        return prestines

    def get_total_pages(self, total, per_page) -> int:
        """Get total number of pages based on a total count and per page value."""
        total_pages = total / per_page
        return int(round(total_pages, 0))

    def build_from_lists(self, raws:list) -> list:
        """Creates list of hydrated collection objects."""
        prestines = []
        for raw_item in raws:
            new_object = self.collect_model(self.conn, self.cursor)
            new_object.build_from_list(raw_item)
            prestines.append(new_object)
        return prestines

    def int_list_to_sql(self, item_list: list) -> str:
        """Transform a list of ints to a sql safe comma separated string."""
        sql_ids = ""
        for i in item_list:
            sql_ids += "%s," % i
        sql_ids = sql_ids[:-1]
        return sql_ids

    def _get_pagination_where_and(self, where_and: list) -> str:
        """
        Create the where clause for pagination when where and clauses are supplied.
        Note: We append multiple statements with an AND in the sql statement.

        """
        where = False
        where_and_sql = ""
        for where_a in where_and:
            where = True
            op = "="
            if 'op' in where_a:
                op = where_a['op']
            where_and_sql += '%s%s"%s" AND ' % (where_a['field'], op, where_a['value'])

        if where:
            where_and_sql = "WHERE " + where_and_sql
            where_and_sql = where_and_sql[:-4]

        return where_and_sql

    def _get_pagination_order(self, order) -> str:
        """
        Create the order clause for pagination using user supplied arguments or defaulting to
        created_desc DESC.

        """
        order_sql = "ORDER BY created_ts DESC"
        if not order:
            return order_sql
        order_field = order['field']
        order_op = order['op']
        order_sql = 'ORDER BY %s %s' % (order_field, order_op)
        return order_sql

    def _get_previous_page(self, page: int) -> int:
        """Get the previous page, or first page if below 1."""
        previous = page - 1
        return previous

    def _get_next_page(self, page: int, last_page: int) -> int:
        """Get the next page."""
        next_page = page + 1
        return next_page

    def _get_urls(self, base_url: str, pagination: dict) -> dict:
        """Get urls for pagination."""
        pagination['first_page_url'] = self._clean_url(base_url, pagination['first_page'])
        pagination['last_page_url'] = self._clean_url(base_url, pagination['last_page'])
        pagination['next_page_url'] = self._clean_url(base_url, pagination['next_page'])
        pagination['previous_page_url'] = self._clean_url(base_url, pagination['previous_page'])
        return pagination

    def _clean_url(self, base_url, url: str) -> str:
        """Clean a url so its pretty and valid."""
        url =  "%s/%s" % (base_url, url)
        url = url.replace('//', '/')
        if url[0] != '/':
            url = '/' + url
        return url


# End File: lan-nanny/lan_nanny/modules/collections/base.py
