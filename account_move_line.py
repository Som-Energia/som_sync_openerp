# coding=utf-8
from osv import osv
from som_sync import SomSync


class AccountMoveLine(osv.osv):
    _name = 'account.move.line'
    _inherit = 'account.move.line'

    FIELDS_TO_SYNC = ['name', 'account_id', 'move_id', 'date_maturity', 'partner_id', 'debit', 'credit']

    def mapping(self, cr, uid, ids, vals):
        values = {}
        if any(k in vals for k in self.FIELDS_TO_SYNC):
            values = {key: vals[key] for key in vals if key in self.FIELDS_TO_SYNC}
        if 'partner_id' in values and values['partner_id'] and not isinstance(values['partner_id'], int):
            partner_id = values['partner_id'][0]
            values['partner_id'] = partner_id
        if 'account_id' in values and values['account_id'] and not isinstance(values['account_id'], int):
            account_id = values['account_id'][0]
            values['account_id'] = account_id
        if 'move_id' in values and values['move_id'] and not isinstance(values['move_id'], long):
            move_id = values['move_id'][0]
            values['move_id'] = move_id
        return values

    def create(self, cr, uid, vals, context={}):
        ids = super(AccountMoveLine, self).create(cr, uid, vals, context=context)
        values = self.mapping(cr, uid, ids, vals)
        if values:
            sync = self.pool.get('som.sync')
            context['check_move_validity'] = False
            context['prev_txid'] = cr.txid
            sync.syncronize(cr, uid, 'account.move.line', 'create', ids, values, context)
        return ids
                                                                           
    def write(self, cr, uid, ids, vals, context={}, check=True, update_check=True):
        super(AccountMoveLine, self).write(cr, uid, ids, vals, context=context,
            check=check, update_check=update_check)
        values = self.mapping(cr, uid, ids, vals)
        if values:
            sync = self.pool.get('som.sync')
            context['prev_txid'] = cr.txid
            sync.syncronize(cr, uid, 'account.move.line', 'write', ids, values, check, update_check,
                context=context)
        return True

    def unlink(self, cr, uid, ids, context={}):
        super(AccountMoveLine, self).unlink(cr, uid, ids, context=context)
        sync = self.pool.get('som.sync')
        context['prev_txid'] = cr.txid
        sync.syncronize(cr, uid, 'account.move.line', 'unlink', ids, {},
            context=context)
        return True

    def force_sync(self, cr, uid, ids, context={}):
        sync = self.pool.get('som.sync')
        context['check_move_validity'] = False
        for id in ids:
            aml_data = self.read(cr, uid, id, self.FIELDS_TO_SYNC)
            aml_data = self.mapping(cr, uid, id, aml_data)
            sync.syncronize(cr, uid, 'account.move.line', 'write', id, aml_data, context)

AccountMoveLine()
