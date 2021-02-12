# coding=utf-8
from osv import osv

class ResPartner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    FIELDS_TO_SYNC = ['name', 'vat']

    def mapping(self, cr, uid, ids, vals):
        values = {}
        if any(k in vals for k in self.FIELDS_TO_SYNC):
            values = {key: vals[key] for key in vals if key in self.FIELDS_TO_SYNC}

        #values['vat_required'] = values['vat']
        #values.pop('vat')
        return values

    def create(self, cr, uid, vals, context=None):
        ids = super(ResPartner, self).create(cr, uid, vals, context=context)
        values = self.mapping(cr, uid, ids, vals)
        if values:
            sync = self.pool.get('som.sync')
            sync.syncronize(cr, uid, 'res.partner', 'create', ids, values)
        return ids
                                                                           
    def write(self, cr, uid, ids, vals, context=None):
        super(ResPartner, self).write(cr, uid, ids, vals, context=context)
        values = self.mapping(cr, uid, ids, vals)
        if values:
            sync = self.pool.get('som.sync')
            sync.syncronize(cr, uid, 'res.partner', 'write', ids, values)
        return True

    def unlink(self, cr, uid, ids, context=None):
        super(ResPartner, self).unlink(cr, uid, ids, context=context)
        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'res.partner', 'unlink', ids, {})
        return True


ResPartner()
