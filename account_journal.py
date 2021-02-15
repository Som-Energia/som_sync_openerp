# coding=utf-8
from osv import osv
from som_sync import SomSync


class AccountJournal(osv.osv):
    _name = 'account.journal'
    _inherit = 'account.journal'

    FIELDS_TO_SYNC = ['name', 'code', 'active', 'type']

    def mapping(self, cr, uid, ids, vals):
        values = {}
        if any(k in vals for k in self.FIELDS_TO_SYNC):
            values = {key: vals[key] for key in vals if key in self.FIELDS_TO_SYNC}
        return values

    def create(self, cr, uid, vals, context=None):
        ids = super(AccountJournal, self).create(cr, uid, vals, context=context)
        values = self.mapping(cr, uid, ids, vals)
        if values:
            sync = self.pool.get('som.sync')
            sync.syncronize(cr, uid, 'account.journal', 'create', ids, values)
        return ids
                                                                           
    def write(self, cr, uid, ids, vals, context=None):
        super(AccountJournal, self).write(cr, uid, ids, vals, context=context)
        values = self.mapping(cr, uid, ids, vals)

        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.journal', 'write', ids, values)
        return True

    def unlink(self, cr, uid, ids, context=None):
        super(AccountJournal, self).unlink(cr, uid, ids, context=context)
        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.journal', 'unlink', ids, {})
        return True


AccountJournal()
