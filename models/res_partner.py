# coding=utf-8
from osv import osv, fields


class ResPartner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    FIELDS_TO_SYNC = ['name', 'vat']

    def mapping(self, cr, uid, ids, vals):
        values = {}
        if any(k in vals for k in self.FIELDS_TO_SYNC):
            values = {key: vals[key] for key in vals if key in self.FIELDS_TO_SYNC}
        return values

    def create(self, cr, uid, vals, context={}):
        ids = super(ResPartner, self).create(cr, uid, vals, context=context)
        values = self.mapping(cr, uid, ids, vals)
        if values:
            sync = self.pool.get('som.sync')
            context['prev_txid'] = cr.txid
            sync.syncronize(cr, uid, 'res.partner', 'create', ids, values,
                context=context)
        return ids

    def write(self, cr, uid, ids, vals, context={}):
        super(ResPartner, self).write(cr, uid, ids, vals, context=context)
        values = self.mapping(cr, uid, ids, vals)
        if values:
            sync = self.pool.get('som.sync')
            context['prev_txid'] = cr.txid
            sync.syncronize(cr, uid, 'res.partner', 'write', ids, values,
                    context=context)
        return True


    def unlink(self, cr, uid, ids, context={}):
        super(ResPartner, self).unlink(cr, uid, ids, context=context)
        sync = self.pool.get('som.sync')
        context['prev_txid'] = cr.txid
        sync.syncronize(cr, uid, 'res.partner', 'unlink', ids, {},
                context=context)
        return True

    def force_sync(self, cr, uid, ids, context={}):
        sync = self.pool.get('som.sync')
        for id in ids:
            rp_data = self.read(cr, uid, id, self.FIELDS_TO_SYNC)
            rp_data = self.mapping(cr, uid, id, rp_data)
            sync.syncronize(cr, uid, 'res.partner', 'write', id, rp_data)

    _columns = {
        'odoo_id':  fields.integer('Odoo id'),
    }

ResPartner()
