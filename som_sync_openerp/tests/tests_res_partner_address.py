# -*- coding: utf-8 -*-
from destral import testing


class TestResPartnerAddress(testing.OOTestCaseWithCursor):

    def setUp(self):
        self.rp_obj = self.openerp.pool.get("res.partner.address")
        self.imd_obj = self.openerp.pool.get("ir.model.data")
        super(TestResPartnerAddress, self).setUp()

    def test_get_endpoint_suffix(self):
        partner_id = self.imd_obj.get_object_reference(
            self.cursor, self.uid, "base", "res_partner_agrolait"
        )[1]

        suffix = self.rp_obj.get_endpoint_suffix(self.cursor, self.uid, partner_id)

        self.assertEqual(suffix, 'other/ES72789709E')
