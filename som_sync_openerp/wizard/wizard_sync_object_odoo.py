# -*- coding: utf-8 -*-
from osv import osv, fields


class WizardSyncObjectOdoo(osv.osv_memory):
    _name = 'wizard.sync.object.odoo'
    _description = 'Wizard to sync object with Odoo'

    def action_sync(self, cursor, uid, ids, context=None):
        if context is None:
            context = {}
        from_model = context.get('from_model')
        active_ids = context.get('active_ids', [])

        if not from_model or not active_ids:
            return {'type': 'ir.actions.act_window_close'}

        sync_obj = self.pool.get('odoo.sync')
        # Support execution from model odoo.sync
        if from_model == 'odoo.sync':
            for _id in active_ids:
                sync_data = sync_obj.browse(cursor, uid, _id)
                from_res_model = sync_data.model.model
                erp_id = sync_data.res_id
                sync_obj.syncronize_sync(
                    cursor, uid, from_res_model, 'sync', erp_id, context=context
                )
            return {'type': 'ir.actions.act_window_close'}

        for record_id in active_ids:
            sync_obj.syncronize_sync(
                cursor, uid, from_model, 'sync', record_id, context=context
            )

        return {'type': 'ir.actions.act_window_close'}

    _columns = {
        "state": fields.selection([("init", "Init"), ("end", "End")], "State"),
        "info": fields.text("Description"),
    }

    _defaults = {
        "state": lambda *a: "init",
    }


WizardSyncObjectOdoo()
