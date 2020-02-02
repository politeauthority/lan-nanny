"""Base Collection

"""


class Base:

    def __init__(self, conn=None, cursor=None):
        """Base collection constructor."""
        self.conn = conn
        self.cursor = cursor

        self.table_name = None
        self.collect_model = None

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
        raw_scans = self.cursor.fetchall()
        scan_logs = []
        for raw_scan in raw_scans:
            scan = self.collect_model(self.conn, self.cursor)
            scan.build_from_list(raw_scan)
            scan_logs.append(scan)
        return scan_logs

    def get_pagination(self, base_url: str, page: int, per_page: int) -> dict:
        """Get numeric count of table rows."""
        pagination = {}
        pagination['total_units'] = self.get_total_count()
        pagination['first_page'] = 1
        pagination['current_page'] = page
        pagination['last_page'] = self.get_total_pages(pagination['total_units'], per_page)
        pagination['next_page'] = self._get_next_page(page, pagination['last_page'])
        pagination['previous_page'] = self._get_previous_page(page)
        pagination['base_url'] = base_url
        pagination = self._get_urls(base_url, pagination)
        return pagination

    def get_total_count(self) -> int:
        """Get numeric count of table rows."""
        sql = """
            SELECT COUNT(*)
            FROM %s;
            """ % self.table_name

        self.cursor.execute(sql)
        raw_scans_count = self.cursor.fetchone()
        return raw_scans_count[0]

    def get_total_pages(self, total, per_page) -> int:
        """Get total number of pages based on a total count and per page value."""
        total_pages = total / per_page
        return int(round(total_pages, 0))

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
