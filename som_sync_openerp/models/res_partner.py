#  -*- coding: utf-8 -*-
from osv import osv


class ResPartner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    MAPPING_FIELDS_TO_SYNC = {
        'name': 'name',
    }
    # TODO: Add foreign keys when API doc is available
    MAPPING_FK = {
    }

    def get_endpoint_suffix(self, cr, uid, id, context={}):
        partner = self.browse(cr, uid, id, context=context)
        if partner.vat:
            # TODO: check with API doc when available
            res = '{}'.format(partner.vat)
            return res
        else:
            return False

    def create(self, cr, uid, vals, context={}):
        ids = super(ResPartner, self).create(cr, uid, vals, context=context)

        # TODO: Uncomment when ready to sync partners
        # sync_obj = self.pool.get('odoo.sync')
        # res = sync_obj.syncronize_sync(
        #     cr, uid, self._name, 'create', ids, context=context)

        return ids


ResPartner()
