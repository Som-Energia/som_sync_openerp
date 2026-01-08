# -*- coding: utf-8 -*-
from destral import testing
from mock import MagicMock, call, ANY


class TestWizardSyncObjectOdoo(testing.OOTestCaseWithCursor):
    def setUp(self):
        self.wizard_obj = self.openerp.pool.get('wizard.sync.object.odoo')
        self.sync_obj = self.openerp.pool.get('odoo.sync')
        self.imd_obj = self.openerp.pool.get("ir.model.data")
        super(TestWizardSyncObjectOdoo, self).setUp()

    def test_action_sync__res_partner(self):
        # Mock syncronize_sync method
        self.sync_obj.syncronize_sync = MagicMock()

        context = {
            'from_model': 'res.partner',
            'active_ids': [1, 2, 3]
        }
        wiz_id = self.wizard_obj.create(self.cursor, self.uid, {}, context=context)
        self.wizard_obj.action_sync(self.cursor, self.uid, [wiz_id], context=context)

        # Verify syncronize_sync was called for each id
        self.assertEqual(self.sync_obj.syncronize_sync.call_count, 3)

        # Verify arguments of the last call
        self.sync_obj.syncronize_sync.assert_called_with(
            self.cursor, self.uid, 'res.partner', 'sync', 3, context=context
        )

    def test_action_sync__odoo_sync(self):
        osdemo_1 = self.imd_obj.get_object_reference(
            self.cursor, self.uid, "som_sync_openerp", "odoo_sync_demo_1"
        )[1]
        osdemo_2 = self.imd_obj.get_object_reference(
            self.cursor, self.uid, "som_sync_openerp", "odoo_sync_demo_2"
        )[1]
        osdemo_3 = self.imd_obj.get_object_reference(
            self.cursor, self.uid, "som_sync_openerp", "odoo_sync_demo_3"
        )[1]

        # Mock syncronize_sync method
        self.sync_obj.syncronize_sync = MagicMock()

        context = {
            'from_model': 'odoo.sync',
            'active_ids': [osdemo_1, osdemo_2, osdemo_3]
        }
        wiz_id = self.wizard_obj.create(self.cursor, self.uid, {}, context=context)
        self.wizard_obj.action_sync(self.cursor, self.uid, [wiz_id], context=context)

        # Verify syncronize_sync was called for each id
        self.assertEqual(self.sync_obj.syncronize_sync.call_count, 3)

        # Verify arguments of the last call
        self.sync_obj.syncronize_sync.has_calls(
            call(ANY, self.uid, u'res.partner', 'sync', 2, context=context),
            call(ANY, self.uid, u'res.country', 'sync', 2, context=context),
            call(ANY, self.uid, u'res.country.state', 'sync', 5, context=context),
        )
