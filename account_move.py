# coding=utf-8
from osv import osv
from som_sync import SomSync


class AccountMove(osv.osv):
    _name = 'account.move'
    _inherit = 'account.move'

    FIELDS_TO_SYNC = ['name', 'date', 'journal_id', 'state', 'partner_id', 'amount']

    def mapping(self, cr, uid, ids, vals):
        values = {}
        if any(k in vals for k in self.FIELDS_TO_SYNC):
            values = {key: vals[key] for key in vals if key in self.FIELDS_TO_SYNC}
        if 'journal_id' in values and values['journal_id'] and not isinstance(values['journal_id'], int):
            journal_id = values ['journal_id'][0]
            values['journal_id'] = journal_id
        if 'partner_id' in values and values['partner_id'] and not isinstance(values['partner_id'], int):
            partner_id = values ['partner_id'][0]
            values['partner_id'] = partner_id
        return values

    def create(self, cr, uid, vals, context={}):
        ids = super(AccountMove, self).create(cr, uid, vals, context=context)
        values = self.mapping(cr, uid, ids, vals)
        if values:
            sync = self.pool.get('som.sync')
            sync.syncronize(cr, uid, 'account.move', 'create', ids, values, context)
        return ids

    def write(self, cr, uid, ids, vals, context={}):
        super(AccountMove, self).write(cr, uid, ids, vals, context=context)
        values = self.mapping(cr, uid, ids, vals)
        if values:
            sync = self.pool.get('som.sync')
            context['prev_txid'] = cr.txid
            sync.syncronize(cr, uid, 'account.move', 'write', ids, values,
                    context=context)
        return True

    def unlink(self, cr, uid, ids, context={}):
        super(AccountMove, self).unlink(cr, uid, ids, context=context)
        sync = self.pool.get('som.sync')
        context['prev_txid'] = cr.txid
        sync.syncronize(cr, uid, 'account.move', 'unlink', ids, {},
                context=context)
        return True

    def force_sync(self, cr, uid, ids, context={}):
        sync = self.pool.get('som.sync')
        for id in ids:
            am_data = self.read(cr, uid, id, self.FIELDS_TO_SYNC)
            am_data = self.mapping(cr, uid, id, am_data)
            sync.syncronize(cr, uid, 'account.move', 'write', id, am_data)

    _columns = {
        'odoo_id':  fields.integer('Odoo id'),
    }

AccountMove()
