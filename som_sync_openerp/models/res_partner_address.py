#  -*- coding: utf-8 -*-
from osv import osv


class ResPartnerAddress(osv.osv):
    _name = 'res.partner.address'
    _inherit = 'res.partner.address'

    MAPPING_FIELDS_TO_SYNC = {
        'name': 'name',
        # 'type': 'type', not mapped, is a constant
        'email': 'email',
        'phone': 'phone',
        'street': 'street',
        'zip': 'code_zip',
    }
    # TODO: Add foreign keys when API doc is available
    MAPPING_FK = {
        'municipi_id': 'res.municipi',
    }

    MAPPING_CONSTANTS = {
        'type': 'invoice',
        'is_company': False,
    }

    def get_endpoint_suffix(self, cr, uid, id, context={}):
        partner = self.browse(cr, uid, id, context=context)
        if partner.partner_id.vat:
            # TODO: check with API doc when available
            res = '{}'.format(partner.partner_id.vat)
            return res
        else:
            return False

    def create(self, cr, uid, vals, context={}):
        ids = super(ResPartnerAddress, self).create(cr, uid, vals, context=context)

        # TODO: Uncomment when ready to sync partners
        # sync_obj = self.pool.get('odoo.sync')
        # res = sync_obj.syncronize_sync(
        #     cr, uid, self._name, 'create', ids, context=context)

        return ids


ResPartnerAddress()
