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

    def get_all(self) -> list:
        """Gets all of a models instances from the database."""
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

    def get_by_ids(self, model_ids: list) -> list:
        model_ids = list(set(model_ids))
        sql_ids = ""
        for i in model_ids:
            sql_ids += "%s," % i
        sql_ids = sql_ids[:-1]
        sql = """
            SELECT *
            FROM %(table_name)s
            WHERE id IN (%(ids)s); """ % {
        'table_name': self.table_name,
        'ids': sql_ids,
        }
        self.cursor.execute(sql)
        raw = self.cursor.fetchall()
        prestine = []
        for raw_item in raw:
            new_object = self.collect_model(self.conn, self.cursor)
            new_object.build_from_list(raw_item)
            prestine.append(new_object)
        return prestine

    def get_all_paginated(self, limit: int=20, offset: int=0) -> list:
        """Get paginated set run logs."""
        sql_vars = {
            'table_name': self.table_name,
            'limit': limit,
            'offset': offset,
        }
        sql = """
            SELECT *
            FROM %(table_name)s
            ORDER BY created_ts DESC
            LIMIT %(limit)s OFFSET %(offset)s;""" % sql_vars
        self.cursor.execute(sql)
        raw = self.cursor.fetchall()
        prestine = []
        for raw_item in raw:
            new_object = self.collect_model(self.conn, self.cursor)
            new_object.build_from_list(raw_item)
            prestine.append(new_object)
        return prestine

    def get_pagination(self, base_url: str, page: int, per_page: int) -> dict:
        """Get numeric count of table rows."""
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

    def build_models_from_list(self, raws:list) -> list:
        """Creates list of hydrated collection objects."""
        prestine = []
        for raw_item in raws:
            new_object = self.collect_model(self.conn, self.cursor)
            new_object.build_from_list(raw_item)
            prestine.append(new_object)
        return prestine

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
