from odoo_rpc_client import Client
from oorq.decorators import job
from osv import osv, fields
from tools import config


class SomSync(osv.osv_memory):
    "Sync manager"

    _name = "som.sync"
    _description = 'Syncronization manager'


    def __init__(self, cursor, uid, context=None):
        self.client = Client(
            host=config.get('odoo_host', 'todoo.somenergia.lan'),
            dbname=config.get('odoo_dbname', 'odoo'),
            user=config.get('odoo_user', 'admin'),
            pwd=config.get('odoo_pwd', 'admin'),
            port=config.get('odoo_port', 80)
        )
        self.context = context


    @job(queue='sync_odoo')
    def syncronize(self, cursor, uid, model, action, vals):
        if action == 'create':
           self.client.execute(model, action, vals)
        elif action == 'write':
            odoo_id = self.client.execute(model, search, [('openerp_id', '=', vals['openerp_id')])
            if odoo_id:
                self.client.execute(model, action, odoo_id, vals)
            else:
                self.client.execute(model, 'create', vals)
        elif action == 'unlink':
            odoo_id = self.client.execute(model, search, [('openerp_id', '=', vals['openerp_id')])
            if odoo_id:
                self.client.execute(model, action, odoo_id)


SomSync()
