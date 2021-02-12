# coding=utf-8
from osv import osv
from som_sync import SomSync


class AccountMove(osv.osv):
    _name = 'account.move'
    _inherit = 'account.move'


    def mapping(self, cr, uid, move_id):
        values = self.read(cr, uid, move_id, ['name', 'date', 'journal_id',
            'state', 'partner_id'])
        #TODO
        #values['openerp_id'] = partner_id
        #values['vat_required'] = values['vat']
        #values.pop('vat')
        return values

    def create(self, cr, uid, vals, context=None):
        move_id = super(AccountMove, self).create(cr, uid, vals, context=context)
        values = self.mapping(cr, uid, move_id)

        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.move', 'create', values)
        return move_id
                                                                           
    def write(self, cr, uid, ids, vals, context=None):
        move_id = super(AccountMove, self).write(cr, uid, ids, vals, context=context)
        values = self.mapping(cr, uid, move_id)

        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.move', 'write', values)
        return move_id

    def unlink(self, cr, uid, ids, context=None):
        super(AccountMove, self).unlink(cr, uid, ids, context=context)

        values = {'openerp_id': ids}
        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.move', 'unlink', values)
        return True


AccountMove()
