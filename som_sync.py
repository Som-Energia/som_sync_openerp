from odoo_rpc_client import Client
from oorq.decorators import job
from osv import osv, fields
from tools import config


class SomSync(osv.osv_memory):
    "Sync manager"

    _name = "som.sync"
    _description = 'Syncronization manager'


    def get_connection(self):
        self.client = Client(
            host=config.get('odoo_host', 'todoo.somenergia.lan'),
            dbname=config.get('odoo_dbname', 'odoo'),
            user=config.get('odoo_user', 'admin'),
            pwd=config.get('odoo_pwd', 'admin'),
            port=config.get('odoo_port', 80)
        )


    def mapping_fk(self, cursor, uid, vals):
        if 'partner_id' in vals:
            vals['partner_id'] = self.client.execute(
                'res.partner', 'search', [('openerp_id', '=', vals['partner_id'])])
        if 'account_id' in vals:
            vals['account_id'] = self.client.execute(
                'account.account', 'search', [('openerp_id', '=', vals['account_id'])])
        if 'move_id' in vals:
            vals['move_id'] = self.client.execute(
                'account.move', 'search', [('openerp_id', '=', vals['move_id'])])

        return vals

    @job(queue='sync_odoo')
    def syncronize(self, cursor, uid, model, action, openerp_ids, vals):
        self.get_connection()
        vals = self.mapping_fk(cursor, uid, vals)

        if action == 'create':
            vals['openerp_id'] = openerp_ids
            self.client.execute(model, action, vals)
        elif action == 'write':
            odoo_id = self.client.execute(model, 'search', [('openerp_id', 'in', openerp_ids)])
            for n in odoo_id:
                self.client.execute(model, action, n, vals)
            if not odoo_id:
                self.client.execute(model, 'create', vals)
        elif action == 'unlink':
            odoo_id = self.client.execute(model, 'search', [('openerp_id', 'in', openerp_ids)])
            for n in odoo_id:
                self.client.execute(model, action, n)


SomSync()
