from __future__ import annotations

import unittest

from gm_gsa.live_accounts import ClientAccount, eligible_live_accounts


class LiveAccountTests(unittest.TestCase):
    def test_filters_manager_test_and_marker(self):
        accounts = [
            ClientAccount("1111111111", "Alpha - live", 1, False, False, "ENABLED"),
            ClientAccount("2222222222", "Beta", 1, False, False, "ENABLED"),
            ClientAccount("3333333333", "Manager - live", 0, True, False, "ENABLED"),
            ClientAccount("4444444444", "Test - live", 1, False, True, "ENABLED"),
        ]
        result = eligible_live_accounts(accounts)
        self.assertEqual([item.customer_id for item in result], ["1111111111"])


if __name__ == "__main__":
    unittest.main()

