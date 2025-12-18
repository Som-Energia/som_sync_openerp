#  -*- coding: utf-8 -*-
from osv import osv, fields


class ResPartner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    FIELDS_TO_SYNC = ['name', 'vat']
    MAPPING_FIELDS_TO_SYNC = {
        'name': 'name'
    }
    MAPPING_FK  = {
        'partner_id': 'res.partner',
    }

    def get_endpoint_suffix(self, cr, uid, id, context={}):
        partner = self.browse(cr, uid, id, context=context)
        if partner.vat:
            # TODO: check with API doc
            res = '{}'.format(partner.vat)
            return res
        else:
            return False

ResPartner()
