# -*- coding: utf-8 -*-
from destral import testing


class TestAccountAccount(testing.OOTestCaseWithCursor):

    def setUp(self):
        self.rcs_obj = self.openerp.pool.get("account.account")
        self.imd_obj = self.openerp.pool.get("ir.model.data")
        super(TestAccountAccount, self).setUp()

    def test_get_endpoint_suffix(self):
        account_id = self.imd_obj.get_object_reference(
            self.cursor, self.uid, "account", "account_unpaid"
        )[1]

        suffix = self.rcs_obj.get_endpoint_suffix(self.cursor, self.uid, account_id)

        self.assertEqual(suffix, '412345')
