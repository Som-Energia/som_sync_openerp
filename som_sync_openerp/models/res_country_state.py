#  -*- coding: utf-8 -*-
from osv import osv
from som_sync_openerp.models.odoo_sync import FF_ENABLE_ODOO_SYNC


class ResCountryState(osv.osv):
    _name = 'res.country.state'
    _inherit = 'res.country.state'

    MAPPING_FIELDS_TO_SYNC = {
        'name': 'name',
        'ree_code': 'code',
        'country_id': 'country_id',
        'id': 'pnt_erp_id',
    }
    MAPPING_FK  = {
        'country_id': 'res.country',
    }

    def get_endpoint_suffix(self, cr, uid, id, context={}):
        state = self.browse(cr, uid, id, context=context)
        if state.ree_code and state.country_id:
            res = '{}/{}'.format(state.country_id.code, state.ree_code)
            return res
        else:
            return False

    def create(self, cr, uid, vals, context={}):
        ids = super(ResCountryState, self).create(cr, uid, vals, context=context)
        if FF_ENABLE_ODOO_SYNC:
            sync_obj = self.pool.get('odoo.sync')
            res = sync_obj.syncronize_sync(
                cr, uid, self._name, 'create', ids, context=context)
        return ids

ResCountryState()
