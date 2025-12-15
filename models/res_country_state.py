#  -*- coding: utf-8 -*-
from osv import osv


class ResCountryState(osv.osv):
    _name = 'res.country.state'
    _inherit = 'res.country.state'

    FIELDS_TO_SYNC = ['name', 'ree_code']
    FIELDS_FK = ['country_id']

    def get_odoo_url(self, cr, uid, id, context={}):
        state = self.browse(cr, uid, id, context=context)
        if state.ree_code and state.country_id:
            url = '{}/{}'.format(state.country_id.code, state.ree_code)
            return url
        else:
            return False


    def create(self, cr, uid, vals, context={}):
        ids = super(ResCountryState, self).create(cr, uid, vals, context=context)
        values = {key: vals[key] for key in vals if key in self.FIELDS_TO_SYNC}
        if values:
            sync = self.pool.get('odoo.sync')
            context['prev_txid'] = cr.txid

            odoo_id = sync.exist(cr, uid, 'res.country.state', url, context=context)
            if odoo_id:
                sync.update_odoo_id(cr, uid, 'res.country.state', ids, odoo_id, context=context)
            else:
                sync.syncronize(cr, uid, 'res.country.state', 'create', ids, values,
                
                context=context)
        return ids

ResCountryState()
