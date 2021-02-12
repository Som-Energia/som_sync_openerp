# coding=utf-8
from osv import osv
from som_sync import SomSync


class AccountMoveLine(osv.osv):
    _name = 'account.move.line'
    _inherit = 'account.move.line'


    def mapping(self, cr, uid, line_id):
        values = self.read(cr, uid, line_id, ['name', 'account_id', 'move_id',
            'date_maturity', 'partner_id'])

        sync.synconize('search', [('openerp_id','=',values['account_id'])
        values_fk = {}
        values_fk = {'partner_id': values['partner_id']}
        #TODO
        #values['openerp_id'] = partner_id
        #values['vat_required'] = values['vat']
        #values.pop('vat')
        return values

    def create(self, cr, uid, vals, context=None):
        line_id = super(AccountMoveLine, self).create(cr, uid, vals, context=context)
        values = self.mapping(cr, uid, line_id)

        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.move.line', 'create', values)
        return line_id
                                                                           
    def write(self, cr, uid, ids, vals, context=None):
        line_id = super(AccountMoveLine, self).write(cr, uid, ids, vals, context=context)
        values = self.mapping(cr, uid, line_id)

        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.move.line', 'write', values)
        return partner_id

    def unlink(self, cr, uid, ids, context=None):
        super(AccountMoveLine, self).unlink(cr, uid, ids, context=context)

        values = {'openerp_id': ids}
        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'account.move.line', 'unlink', values)
        return True


AccountMoveLine()
