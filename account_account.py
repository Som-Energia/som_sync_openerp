# coding=utf-8
from osv import osv
from som_sync import SomSync


class AccountAccount(osv.osv):
    _name = 'account.account'
    _inherit = 'account.account'

    FIELDS_TO_SYNC = ['name', 'code', 'user_type']

    def mapping(self, cr, uid, ids, vals):
        values = {}
        if any(k in vals for k in self.FIELDS_TO_SYNC):
            values = {key: vals[key] for key in vals if key in self.FIELDS_TO_SYNC}
        user_type = ''
        if not 'user_type' in values:
            user_type =  self.read(cr, uid, ids, ['user_type'])[0]['user_type'][0]
        else:
            user_type = values['user_type'][0]
            values.pop('user_type')
        values['user_type_id'] = user_type
        return values

    def create(self, cr, uid, vals, context=None):
        ids = super(AccountAccount, self).create(cr, uid, vals, context=context)
        values = self.mapping(cr, uid, ids, vals)
        if values:
            sync = self.pool.get('som.sync')
            sync.syncronize(cr, uid, 'account.account', 'create', ids, values)
        return ids
                                                                           
    def write(self, cr, uid, ids, vals, context=None):
        super(AccountAccount, self).write(cr, uid, ids, vals, context=context)
        values = self.mapping(cr, uid, ids, vals)

        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.account', 'write', ids, values)
        return True

    def unlink(self, cr, uid, ids, context=None):
        super(AccountAccount, self).unlink(cr, uid, ids, context=context)
        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.account', 'unlink', ids, {})
        return True

    def force_sync(self, cr, uid, ids, context=None):
        sync = self.pool.get('som.sync')
        for id in ids:
            aa_data = self.read(cr, uid, id, self.FIELDS_TO_SYNC)
            aa_data = self.mapping(cr, uid, id, aa_data)
            sync.syncronize(cr, uid, 'account.account', 'create', id, aa_data)

AccountAccount()

class AccountAccountType(osv.osv):
    _name = 'account.account.type'
    _inherit = 'account.account.type'

    FIELDS_TO_SYNC = ['name']

    def mapping(self, cr, uid, ids, vals):
        values = {}
        if any(k in vals for k in self.FIELDS_TO_SYNC):
            values = {key: vals[key] for key in vals if key in self.FIELDS_TO_SYNC}
        values['type'] = 'other'
        return values

    def create(self, cr, uid, vals, context=None):
        ids = super(AccountAccountType, self).create(cr, uid, vals, context=context)
        values = self.mapping(cr, uid, ids, vals)
        if values:
            sync = self.pool.get('som.sync')
            sync.syncronize(cr, uid, 'account.account.type', 'create', ids, values)
        return ids

    def write(self, cr, uid, ids, vals, context=None):
        super(AccountAccountType, self).write(cr, uid, ids, vals, context=context)
        values = self.mapping(cr, uid, ids, vals)

        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.account.type', 'write', ids, values)
        return True

    def unlink(self, cr, uid, ids, context=None):
        super(AccountAccountType, self).unlink(cr, uid, ids, context=context)
        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.account.type', 'unlink', ids, {})
        return True


AccountAccountType()
