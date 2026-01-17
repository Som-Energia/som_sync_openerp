# -*- coding: utf-8 -*-
from osv import osv, fields
from som_sync_openerp.models.odoo_sync import STATIC_MODELS


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
        wiz = self.browse(cursor, uid, ids[0], context=context)
        if from_model == 'odoo.sync':
            for _id in active_ids:
                sync_data = sync_obj.browse(cursor, uid, _id)
                from_res_model = sync_data.model.model
                erp_id = sync_data.res_id
                sync_obj.syncronize_sync(
                    cursor, uid, from_res_model, 'sync', erp_id, context=context
                )
            return {'type': 'ir.actions.act_window_close'}
        elif wiz.is_static:
            context['odoo_id'] = wiz.odoo_id
            sync_obj.syncronize_sync(
                cursor, uid, from_model, 'sync', active_ids[0], context=context
            )
            return {'type': 'ir.actions.act_window_close'}

        for record_id in active_ids:
            sync_obj.syncronize_sync(
                cursor, uid, from_model, 'sync', record_id, context=context
            )

        return {'type': 'ir.actions.act_window_close'}

    def _get_default_value(self, cursor, uid, context=None):
        if context is None:
            context = {}
        from_model = context.get('from_model')
        return from_model in STATIC_MODELS

    _columns = {
        "state": fields.selection([("init", "Init"), ("end", "End")], "State"),
        "info": fields.text("Description"),
        "is_static": fields.boolean("Is Static Model"),
        "odoo_id": fields.integer("Odoo ID"),
    }

    _defaults = {
        "state": lambda *a: "init",
        "is_static": _get_default_value,
    }


WizardSyncObjectOdoo()
