#  -*- coding: utf-8 -*-
from osv import osv


class ResCountry(osv.osv):
    _name = 'res.country'
    _inherit = 'res.country'

    FIELDS_TO_SYNC = ['name', 'code']
    MAPPING_FIELDS_TO_SYNC = {
        'name': 'name',
        'code': 'code',
    }
    MAPPING_FK  = {
    }

    def get_endpoint_suffix(self, cr, uid, id, context={}):
        country = self.browse(cr, uid, id, context=context)
        if country.code:
            res = '{}'.format(country.code)
            return res
        else:
            return False

    def create(self, cr, uid, vals, context={}):
        ids = super(ResCountry, self).create(cr, uid, vals, context=context)
        values = {key: vals[key] for key in vals if key in self.FIELDS_TO_SYNC}
        if values:
            pass

        return ids

ResCountry()
