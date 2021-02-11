# coding=utf-8
from osv import osv
from som_sync import SomSync


class ResPartner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'


    def mapping(self, cr, uid, partner_id):
        values = self.read(cr, uid, partner_id, ['name', 'vat'])
        #TODO
        #values['openerp_id'] = partner_id
        #values['vat_required'] = values['vat']
        #values.pop('vat')
        return values

    def create(self, cr, uid, vals, context=None):
        partner_id = super(ResPartner, self).create(cr, uid, vals, context=context)
        values = self.mapping(cr, uid, partner_id)

        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'res.partner', 'create', values)
        return partner_id
                                                                           
    def write(self, cr, uid, ids, vals, context=None):
        partner_id = super(ResPartner, self).write(cr, uid, ids, vals, context=context)
        values = self.mapping(cr, uid, partner_id)

        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'res.partner', 'write', values)
        return partner_id

    def unlink(self, cr, uid, ids, context=None):
        super(ResPartner, self).unlink(cr, uid, ids, context=context)

        values = {'openerp_id': ids}
        sync = self.pool.get('som.sync')
        sync.syncronize(cr, uid, 'res.partner', 'unlink', values)
        return True


ResPartner()
