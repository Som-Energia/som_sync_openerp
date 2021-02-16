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
            port=config.get('odoo_port', 8080)
        )

    def second_oportunity(self, cursor, uid, vals, model, field):
        Model = self.pool.get(model)
        values = Model.read(cursor, uid, vals[field], Model.FIELDS_TO_SYNC)
        values = Model.mapping(cursor, uid, vals[field], values)
        vals2 = self.mapping_fk(cursor, uid, model, values)
        vals2['openerp_id'] = vals[field]
        return self.client.execute(model, 'create', vals2)

    def mapping_fk(self, cursor, uid, model, vals):
        if 'partner_id' in vals:
            try:
                vals['partner_id'] = self.client.execute(
                    'res.partner', 'search', [('openerp_id', '=', vals['partner_id'])])[0]
            except IndexError:
                partner_id = self.second_oportunity(cursor, uid, vals, 'res.partner', 'partner_id')
                vals['partner_id'] = self.client.execute(
                    'res.partner', 'search', [('openerp_id', '=', vals['partner_id'])])[0]
        if 'account_id' in vals:
            try:
                vals['account_id'] = self.client.execute(
                    'account.account', 'search', [('openerp_id', '=', vals['account_id'])])[0]
            except IndexError:
                account_id = self.second_oportunity(cursor, uid, vals, 'account.account', 'account_id')
                vals['account_id'] = self.client.execute(
                    'account.account', 'search', [('openerp_id', '=', vals['account_id'])])[0]
        if 'move_id' in vals:
            try:
                vals['move_id'] = self.client.execute(
                    'account.move', 'search', [('openerp_id', '=', vals['move_id'])])[0]
            except IndexError:
                move_id = self.second_oportunity(cursor, uid, vals, 'account.move', 'move_id')
                vals['move_id'] = self.client.execute(
                    'account.move', 'search', [('openerp_id', '=', vals['move_id'])])[0]
        if 'user_type_id' in vals:
            try:
                vals['user_type_id'] = self.client.execute(
                    'account.account.type', 'search', [('openerp_id', '=', vals['user_type_id'])])[0]
            except IndexError:
                type_id = self.second_oportunity(cursor, uid, vals, 'account.account.type', 'user_type_id')
                vals['user_type_id'] = self.client.execute(
                    'account.account.type', 'search', [('openerp_id', '=', vals['user_type_id'])])[0]
        if 'journal_id' in vals:
            try:
                vals['journal_id'] = self.client.execute(
                    'account.journal', 'search', [('openerp_id', '=', vals['journal_id'])])[0]
            except IndexError:
                journal_id = self.second_oportunity(cursor, uid, vals, 'account.journal', 'journal_id')
                vals['journal_id'] = self.client.execute(
                    'account.journal', 'search', [('openerp_id', '=', vals['journal_id'])])[0]

        return vals


    @job(queue='sync_odoo')
    def syncronize(self, cursor, uid, model, action, openerp_ids, vals):
        self.get_connection()
        vals = self.mapping_fk(cursor, uid, model, vals)
        if isinstance(openerp_ids, list):
            openerp_ids = openerp_ids[0]

        if action == 'create':
            vals['openerp_id'] = openerp_ids
            self.client.execute(model, action, vals)
        elif action == 'write':
            odoo_id = self.client.execute(model, 'search', [('openerp_id', '=', openerp_ids)])
            for n in odoo_id:
                self.client.execute(model, action, n, vals)
            if not odoo_id:
                Model = self.pool.get(model)
                values = Model.read(cursor, uid, openerp_ids, Model.FIELDS_TO_SYNC)
                vals = Model.mapping(cursor, uid, openerp_ids, values)
                vals = self.mapping_fk(cursor, uid, model, vals)
                vals['openerp_id'] = openerp_ids
                self.client.execute(model, 'create', vals)
        elif action == 'unlink':
            odoo_id = self.client.execute(model, 'search', [('openerp_id', '=', openerp_ids)])
            for n in odoo_id:
                self.client.execute(model, action, n)


SomSync()
