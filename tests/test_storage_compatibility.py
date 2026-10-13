"""Legacy SQLite errors map without hiding unrelated operational failures."""
from pathlib import Path
import sqlite3
import tempfile
import unittest

from koevd_eval.storage import LocalSubmissionStore, StorageError, _operational_failure


class SQLiteCompatibilityTests(unittest.TestCase):
    def test_legacy_errors_without_code_map_exact_known_messages(self):
        for message,expected in [('database or disk is full','store_capacity'),
                                 ('database is locked','store_busy'),
                                 ('database table is locked: requests','store_busy'),
                                 ('database schema is locked: main','store_busy')]:
            with self.subTest(message=message):
                error=sqlite3.OperationalError(message)
                self.assertFalse(hasattr(error,'sqlite_errorcode'))
                self.assertEqual(_operational_failure(error)[0],expected)
        self.assertIsNone(_operational_failure(sqlite3.OperationalError('no such table: private')))

    def test_primary_numeric_result_precedes_message_and_extended_codes(self):
        for code,expected in [(5,'store_busy'),(6,'store_busy'),(13,'store_capacity'),(5|256,'store_busy')]:
            error=sqlite3.OperationalError('unrelated text');error.sqlite_errorcode=code
            self.assertEqual(_operational_failure(error)[0],expected)
        error=sqlite3.OperationalError('database or disk is full');error.sqlite_errorcode=10
        self.assertIsNone(_operational_failure(error))

    def test_legacy_full_failure_rolls_back_and_unknown_error_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            store=LocalSubmissionStore(Path(temporary)/'store')
            with self.assertRaises(StorageError) as failure:
                with store.connection(write=True) as db:
                    db.execute('INSERT INTO artifacts VALUES(?,?,?)',('a'*64,'b'*64,b'fixture'))
                    raise sqlite3.OperationalError('database or disk is full')
            self.assertEqual(failure.exception.code,'store_capacity')
            self.assertEqual(failure.exception.status,507)
            with store.connection() as db:self.assertEqual(db.execute('SELECT count(*) FROM artifacts').fetchone()[0],0)
            with self.assertRaisesRegex(sqlite3.OperationalError,'no such table'):
                with store.connection(write=True):raise sqlite3.OperationalError('no such table: absent')
