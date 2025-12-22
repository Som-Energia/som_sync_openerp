# -*- coding: utf-8 -*-
from destral import testing


class TestResCountryState(testing.OOTestCaseWithCursor):

    def setUp(self):
        self.rcs_obj = self.openerp.pool.get("res.country.state")
        self.imd_obj = self.openerp.pool.get("ir.model.data")
        super(TestResCountryState, self).setUp()

    def test_get_endpoint_suffix(self):
        state_id = self.imd_obj.get_object_reference(
            self.cursor, self.uid, "l10n_ES_toponyms", "ES46"
        )[1]

        suffix = self.rcs_obj.get_endpoint_suffix(self.cursor, self.uid, state_id)

        self.assertEqual(suffix, 'ES/V')
