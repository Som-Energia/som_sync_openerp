# coding=utf-8
from osv import osv
from som_sync import SomSync


class AccountJournal(osv.osv):
    _name = 'account.journal'
    _inherit = 'account.journal'


    def mapping(self, cr, uid, journal_id):
        values = self.read(cr, uid, journal_id, ['name', 'type', 'code'])
        #TODO
        #values['openerp_id'] = partner_id
        #values['vat_required'] = values['vat']
        #values.pop('vat')
        return values

    def create(self, cr, uid, vals, context=None):
        journal_id = super(AccountJournal, self).create(cr, uid, vals, context=context)
        values = self.mapping(cr, uid, journal_id)

        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.journal', 'create', values)
        return journal_id
                                                                           
    def write(self, cr, uid, ids, vals, context=None):
        journal_id = super(AccountJournal, self).write(cr, uid, ids, vals, context=context)
        values = self.mapping(cr, uid, journal_id)

        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.journal', 'write', values)
        return journal_id

    def unlink(self, cr, uid, ids, context=None):
        super(AccountJournal, self).unlink(cr, uid, ids, context=context)

        values = {'openerp_id': ids}
        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.journal', 'unlink', values)
        return True


ResPartner()
