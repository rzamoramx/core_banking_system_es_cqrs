
from unittest import TestCase
from com_ivansoft_corebank_lib.models.Transaction import Transaction
from datetime import datetime


class TestTransaction(TestCase):
    def test_parse_date(self):
        # Arrange
        date = 'Fri Aug 30 18:24:06 CST 2024'
        expected_date = datetime(2024, 8, 30, 18, 24, 6)

        transaction = Transaction(
            id='1',
            accountId='1',
            amount=1000,
            type='DEPOSIT',
            status='PENDING',
            description='Test',
            timestamp=date
        )

        # Act
        result = transaction.timestamp

        # Assert
        self.assertEqual(result, expected_date)
