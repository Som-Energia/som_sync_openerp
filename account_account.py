# coding=utf-8
from osv import osv
from som_sync import SomSync


class AccountAccount(osv.osv):
    _name = 'account.account'
    _inherit = 'account.account'


    def mapping(self, cr, uid, account_id):
        values = self.read(cr, uid, account_id, ['name', 'code'])
        #TODO
        #values['openerp_id'] = partner_id
        #values['vat_required'] = values['vat']
        #values.pop('vat')
        return values

    def create(self, cr, uid, vals, context=None):
        account_id = super(AccountAccount, self).create(cr, uid, vals, context=context)
        values = self.mapping(cr, uid, account_id)

        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.account', 'create', values)
        return account_id
                                                                           
    def write(self, cr, uid, ids, vals, context=None):
        account_id = super(AccountAccount, self).write(cr, uid, ids, vals, context=context)
        values = self.mapping(cr, uid, account_id)

        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.account', 'write', values)
        return partner_id

    def unlink(self, cr, uid, ids, context=None):
        super(AccountAccount, self).unlink(cr, uid, ids, context=context)

        values = {'openerp_id': ids}
        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.account', 'unlink', values)
        return True


AccountAccount()
