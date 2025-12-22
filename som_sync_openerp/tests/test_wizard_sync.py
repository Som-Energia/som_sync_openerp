# -*- coding: utf-8 -*-
from destral import testing
from mock import MagicMock


class TestWizardSyncObjectOdoo(testing.OOTestCaseWithCursor):

    def test_action_sync(self):
        wizard_obj = self.openerp.pool.get('wizard.sync.object.odoo')
        sync_obj = self.openerp.pool.get('odoo.sync')

        # Mock syncronize_sync method
        sync_obj.syncronize_sync = MagicMock()

        context = {
            'from_model': 'res.partner',
            'active_ids': [1, 2, 3]
        }
        wiz_id = wizard_obj.create(self.cursor, self.uid, {}, context=context)
        wizard_obj.action_sync(self.cursor, self.uid, [wiz_id], context=context)

        # Verify syncronize_sync was called for each id
        self.assertEqual(sync_obj.syncronize_sync.call_count, 3)

        # Verify arguments of the last call
        sync_obj.syncronize_sync.assert_called_with(
            self.cursor, self.uid, 'res.partner', 'sync', 3, context=context
        )
