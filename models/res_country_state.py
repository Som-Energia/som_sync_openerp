#  -*- coding: utf-8 -*-
from osv import osv


class ResCountryState(osv.osv):
    _name = 'res.country.state'
    _inherit = 'res.country.state'

    FIELDS_TO_SYNC = ['name', 'ree_code']

    def create(self, cr, uid, vals, context={}):
        ids = super(ResCountryState, self).create(cr, uid, vals, context=context)
        values = {key: vals[key] for key in vals if key in self.FIELDS_TO_SYNC}
        if values:
            sync = self.pool.get('odoo.sync')
            context['prev_txid'] = cr.txid

            url = 'ES/V'
            odoo_id = sync.exist(cr, uid, 'res.country.state', url, context=context)
            if odoo_id:
                sync.update_odoo_id(cr, uid, 'res.country.state', ids, odoo_id, context=context)
            else:
                country_letter = 'ES'
                state_letter = 'V'
                values = {
                    "name": "Valencia",
                    "code": "V",
                    "country_id": 68,
                    "pnt_erp_id": 10001
                }
                sync.syncronize(cr, uid, 'res.country.state', 'create', ids, values,
                
                context=context)
        return ids

ResCountryState()
