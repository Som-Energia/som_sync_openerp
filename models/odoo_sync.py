#  -*- coding: utf-8 -*-
from osv import osv, fields
from oorq.decorators import job
import requests
from datetime import datetime

MAPPING_MODELS_GET = {
    'res.country.state': 'states',
}
MAPPING_MODELS_POST = {
    'res.country.state': 'state',
}

class OdooSync(osv.osv):
    "Sync manager"

    _name = "odoo.sync"
    _description = 'Syncronization manager'

    def _get_conn_params(self, cursor, uid):
        config_obj = self.pool.get('res.config')
        try:
            odoo_url_api = config_obj.get(cursor, uid, 'odoo_url_api', 'http://localhost:8069/api/')
            odoo_api_key = config_obj.get(cursor, uid, 'odoo_api_key', 'secret')
        except Exception as e:
            raise osv.except_osv('Configuration error',
                                    'Odoo connection parameters not found.')
        return odoo_url_api, odoo_api_key

    @job(queue='sync_odoo')
    def syncronize(self, cursor, uid, model, action, openerp_ids, vals, context={}, check=True, update_check=True):
        odoo_url_api, odoo_api_key = self._get_conn_params(cursor, uid)
        if isinstance(openerp_ids, list):
            openerp_ids = openerp_ids[0]

        rp_obj = self.pool.get(model)
        if action == 'create':     
            #TODO: CREATE
            url = odoo_url_api + MAPPING_MODELS_POST.get(model)
            odoo_id = self.exist(cursor, uid, model, url)
            # if odoo_id:
            #     self.update_odoo_id(cursor, uid, )

        elif action == 'write':
            #TODO: WRITE
            print("WRITE SYNC TOODO")
        elif action == 'unlink':
            #TODO: UNLINK
            print("UNLINK SYNC TOODO")

        return True

    def exist(self, cursor, uid, model, url, context={}):
        odoo_url_api, odoo_api_key = self._get_conn_params(cursor, uid)
        url_base = odoo_url_api + MAPPING_MODELS_POST.get(model) + "/" + url
        headers = {
            "X-API-Key": odoo_api_key,
            "Accept": "application/json",
        }
        response = requests.get(url_base, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data and 'success' in data and data['success'] == True:
                return data['data']['odoo_id']
        return False

    def update_odoo_id(self, cursor, uid, model, openerp_id, odoo_id, context={}):
        exist = self.search(cursor, uid,
            [('model.model', '=', model), ('res_id', '=', openerp_id)]
        )
        if not exist:
            self.create(cursor, uid,{
                'model': self.pool.get('ir.model').search(cursor, uid, [('model', '=', model)])[0],
                'res_id': openerp_id,
                'odoo_id': odoo_id,
                'odoo_last_sync_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
            return True

        vals = {
            'odoo_id': odoo_id,
            'odoo_last_sync_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        self.write(cursor, uid, exist, vals, context=context)
        return True


    _columns = {
        'model': fields.many2one('ir.model', 'Model'),
        'res_id':  fields.integer('ERP id'),
        'odoo_id':  fields.integer('Odoo id'),
        'odoo_last_sync_at': fields.datetime('Odoo last sync at'),
        # Aquests camps indiquen la data de creacio i ultima modificacio al Odoo, no la data d'actualitzció de l'odoo_id a OpenERP
        'odoo_created_at': fields.datetime('Odoo created at'),
        'odoo_updated_at': fields.datetime('Odoo updated at'),
        'odoo_last_update_result': fields.text('Odoo last update result'),
    }

    _sql_constraints = [
        ('model_res_id_uniq', 'unique (model,res_id)', ("Model and res_id must be unique"))
    ]

OdooSync()
