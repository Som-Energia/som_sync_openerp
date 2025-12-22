# -*- coding: utf-8 -*-
from __future__ import absolute_import
from destral import testing
from som_sync_openerp.models.odoo_exceptions import CreationNotSupportedException


class TestOdooSync(testing.OOTestCaseWithCursor):

    def setUp(self):
        self.os_obj = self.openerp.pool.get("odoo.sync")
        super(TestOdooSync, self).setUp()

    def test_create_odoo_record__notSupported(self):
        with self.assertRaises(CreationNotSupportedException):
            self.os_obj.create_odoo_record(self.cursor, self.uid, 'res.municipi', {})
