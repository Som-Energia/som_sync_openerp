# -*- coding: utf-8 -*-
from destral import testing


class TestResCountryState(testing.OOTestCaseWithCursor):

    def setUp(self):
        self.pp_obj = self.openerp.pool.get("product.pricelist")
        super(TestResCountryState, self).setUp()

    def test_odoo_sync_exist(self):
        sync = self.openerp.pool.get('odoo.sync')
        url = '/ES/V'
        odoo_id = sync.exist(self.cursor, self.uid, 'res.country.state', url, context={})
        self.assertIsNone(odoo_id)