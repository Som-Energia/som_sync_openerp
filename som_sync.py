from odoo_rpc_client import Client
from oorq.decorators import job
from osv import osv, fields
from tools import config
import time
import netsvc

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
        odoo_id = self.client.execute(model, 'create', vals2)
        rp_obj = self.pool.get(model)
        rp_obj.write(cursor, uid, [vals[field]], {'odoo_id': odoo_id})
        return self.client.execute(model, 'create', vals2)

    def save_odoo_id(self, cursor, uid, id, model, odoo_id):
        if isinstance(id, int):
            id = [id]
        rp_obj = self.pool.get(model)
        rp_obj.write(cursor, uid, id, {'odoo_id': odoo_id})

    def mapping_fk(self, cursor, uid, model, vals):
        if 'partner_id' in vals:
            try:
                rp_obj = self.pool.get('res.partner')
                odoo_id = rp_obj.read(cursor, uid, vals['partner_id'], ['odoo_id'])['odoo_id']
                if not odoo_id:
                    odoo_id = self.client.execute(
                        'res.partner', 'search', [('openerp_id', '=', vals['partner_id'])])[0]
                    self.save_odoo_id(cursor, uid, vals['partner_id'], 'res.partner', odoo_id)
                vals['partner_id'] = odoo_id
            except IndexError:
                self.second_oportunity(cursor, uid, vals, 'res.partner', 'partner_id')
                vals['partner_id'] = self.client.execute(
                    'res.partner', 'search', [('openerp_id', '=', vals['partner_id'])])[0]
        if 'account_id' in vals:
            try:
                rp_obj = self.pool.get('account.account')
                odoo_id = rp_obj.read(cursor, uid, vals['account_id'], ['odoo_id'])['odoo_id']
                if not odoo_id:
                    odoo_id = self.client.execute(
                        'account.account', 'search', [('openerp_id', '=', vals['account_id'])])[0]
                    self.save_odoo_id(cursor, uid, vals['account_id'], 'account.account', odoo_id)
                vals['account_id'] = odoo_id
            except IndexError:
                self.second_oportunity(cursor, uid, vals, 'account.account', 'account_id')
                vals['account_id'] = self.client.execute(
                    'account.account', 'search', [('openerp_id', '=', vals['account_id'])])[0]
        if 'move_id' in vals:
            try:
                rp_obj = self.pool.get('account.move')
                odoo_id = rp_obj.read(cursor, uid, vals['move_id'], ['odoo_id'])['odoo_id']
                if not odoo_id:
                    odoo_id = self.client.execute(
                        'account.move', 'search', [('openerp_id', '=', vals['move_id'])])[0]
                    self.save_odoo_id(cursor, uid, vals['move_id'], 'account.move', odoo_id)
                vals['move_id'] = odoo_id
            except IndexError:
                move_id = self.second_oportunity(cursor, uid, vals, 'account.move', 'move_id')
                vals['move_id'] = self.client.execute(
                    'account.move', 'search', [('openerp_id', '=', vals['move_id'])])[0]
        if 'user_type_id' in vals:
            try:
                rp_obj = self.pool.get('account.account.type')
                odoo_id = rp_obj.read(cursor, uid, vals['user_type_id'], ['odoo_id'])['odoo_id']
                if not odoo_id:
                    odoo_id = self.client.execute(
                        'account.account.type', 'search', [('openerp_id', '=', vals['user_type_id'])])[0]
                    self.save_odoo_id(cursor, uid, vals['user_type_id'], 'account.account.type', odoo_id)
                vals['user_type_id'] = odoo_id
            except IndexError:
                type_id = self.second_oportunity(cursor, uid, vals, 'account.account.type', 'user_type_id')
                vals['user_type_id'] = self.client.execute(
                    'account.account.type', 'search', [('openerp_id', '=', vals['user_type_id'])])[0]
        if 'journal_id' in vals:
            try:
                rp_obj = self.pool.get('account.journal')
                odoo_id = rp_obj.read(cursor, uid, vals['journal_id'], ['odoo_id'])['odoo_id']
                if not odoo_id:
                    odoo_id = self.client.execute(
                        'account.journal', 'search', [('openerp_id', '=', vals['journal_id'])])[0]
                    self.save_odoo_id(cursor, uid, vals['journal_id'], 'account.journal', odoo_id)
                vals['journal_id'] = odoo_id
            except IndexError:
                journal_id = self.second_oportunity(cursor, uid, vals, 'account.journal', 'journal_id')
                vals['journal_id'] = self.client.execute(
                    'account.journal', 'search', [('openerp_id', '=', vals['journal_id'])])[0]

        return vals


    @job(queue='sync_odoo')
    def syncronize(self, cursor, uid, model, action, openerp_ids, vals, context={}, check=True, update_check=True):
        if 'prev_txid' in context:
            seconds = 1
            for n in range(10):
                cursor._obj.execute("select txid_status(%s)", (int(context['prev_txid']),))
                result = cursor._obj.fetchone()[0]
                if result != 'in progress':
                    break
                time.sleep(seconds)
                seconds = seconds * 2

            if result == 'in progress':
                raise Exception("Transaction %d in progress. Sync with Odoo timeout. Retry later" % int(cursor.txid))
            elif result == 'aborted' or not result:
                return True
            elif result != 'committed':
                raise Exception("Unknown error in Postgres txid type: %s" % str(result))

        self.get_connection()
        vals = self.mapping_fk(cursor, uid, model, vals)
        if isinstance(openerp_ids, list):
            openerp_ids = openerp_ids[0]

        rp_obj = self.pool.get(model)
        if action == 'create':            
            odoo_id = rp_obj.read(cursor, uid, openerp_ids, ['odoo_id'])
            if not odoo_id:
                odoo_id = self.client.execute(model, 'search', [('openerp_id', '=', openerp_ids)], context=context)
                if odoo_id:
                    rp_obj.write(cursor, uid, [openerp_ids], {'odoo_id': odoo_id})
            if not odoo_id:
                vals['openerp_id'] = openerp_ids
                new_odoo_id = self.client.execute(model, action, vals, context)
                rp_obj.write(cursor, uid, [openerp_ids], {'odoo_id': new_odoo_id})
        elif action == 'write':
            odoo_id = rp_obj.read(cursor, uid, openerp_ids, ['odoo_id'])['odoo_id']
            if not odoo_id:
                odoo_id = self.client.execute(model, 'search', [('openerp_id', '=', openerp_ids)], context=context)
                if odoo_id:
                    rp_obj.write(cursor, uid, [openerp_ids], {'odoo_id': odoo_id})
            for n in odoo_id:
                new_odoo_id = self.client.execute(model, action, n, vals, context, check, update_check)
            if not odoo_id:
                Model = self.pool.get(model)
                values = Model.read(cursor, uid, openerp_ids, Model.FIELDS_TO_SYNC)
                vals = Model.mapping(cursor, uid, openerp_ids, values)
                vals = self.mapping_fk(cursor, uid, model, vals)
                vals['openerp_id'] = openerp_ids
                self.client.execute(model, 'create', vals, context)
        elif action == 'unlink':
            odoo_id = self.client.execute(model, 'search', [('openerp_id', '=', openerp_ids)], context=context)
            for n in odoo_id:
                self.client.execute(model, action, n, context)


SomSync()
