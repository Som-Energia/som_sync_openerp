# coding=utf-8
from osv import osv
from som_sync import SomSync


class AccountMoveLine(osv.osv):
    _name = 'account.move.line'
    _inherit = 'account.move.line'

    FIELDS_TO_SYNC = ['name', 'account_id', 'move_id', 'date_maturity', 'partner_id']
    def mapping(self, cr, uid, ids, vals):
        values = {}
        if any(k in vals for k in self.FIELDS_TO_SYNC):
            values = {key: vals[key] for key in vals if key in self.FIELDS_TO_SYNC}
        if 'partner_id' in values:
            partner_id = values ['partner_id'][0]
            values ['partner_id'] = partner_id
        if 'account_id' in values:
            account_id = values ['account_id'][0]
            values ['account_id'] = account_id
        if 'move_id' in values:
            move_id = values ['move_id'][0]
            values ['move_id'] = move_id
        return values

    def create(self, cr, uid, vals, context=None):
        ids = super(AccountMoveLine, self).create(cr, uid, vals, context=context)
        values = self.mapping(cr, uid, ids, vals)
        if values:
            sync = self.pool.get('som.sync')
            sync.syncronize(cr, uid, 'account.move.line', 'create', ids, values)
        return ids
                                                                           
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        super(AccountMoveLine, self).write(cr, uid, ids, vals, context=context)
        values = self.mapping(cr, uid, ids, vals)

        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.move.line', 'write', ids, values)
        return True

    def unlink(self, cr, uid, ids, context=None):
        super(AccountMoveLine, self).unlink(cr, uid, ids, context=context)
        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.move.line', 'unlink', ids, {})
        return True

    def force_sync(self, cr, uid, ids, context=None):
        sync = self.pool.get('som.sync')
        for id in ids:
            aml_data = self.read(cr, uid, id, self.FIELDS_TO_SYNC)
            aml_data = self.mapping(cr, uid, id, aml_data)
            sync.syncronize(cr, uid, 'account.move.line', 'create', id, aml_data)

AccountMoveLine()
