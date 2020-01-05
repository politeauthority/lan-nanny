"""Witnesses
Gets collections of Witnesses.

"""
from ..models.witness import Witness


class Witnesses():

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

    def get_by_scan_id(self, scan_id: int) -> list:
        """
        Gets all witness records from a scan_id.

        """
        sql = """
            SELECT *
            FROM witness
            WHERE run_id = %s
            ORDER BY created_ts DESC;""" % scan_id

        self.cursor.execute(sql)
        raw_witnesses = self.cursor.fetchall()
        witnesses = []
        for raw_witness in raw_witnesses:
            witness = Witness(self.conn, self.cursor)
            witness.build_from_list(raw_witness, build_device=True)
            witnesses.append(witness)
        return witnesses

# End File: lan-nanny/modules/collections/witnesses.py
