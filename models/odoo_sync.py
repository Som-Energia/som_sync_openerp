#  -*- coding: utf-8 -*-
from osv import osv, fields
from oorq.decorators import job
import requests
from datetime import datetime

# Get Odoo register
MAPPING_MODELS_GET = {
    'res.country.state': 'state',
    'res.country': 'country',
}
# Update erp_id in Odoo
MAPPING_MODELS_ENTITIES = {
    'res.country.state': 'state',
}
# Create register in Odoo
MAPPING_MODELS_POST = {
    'res.country.state': 'states',
}
MAPPING_FK  = {
    'country_id': 'country',
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
    def syncronize(self, cursor, uid, model, action, openerp_id, vals, context={}, check=True, update_check=True):
        odoo_url_api, odoo_api_key = self._get_conn_params(cursor, uid)
        if isinstance(openerp_id, list):
            openerp_id = openerp_id[0]

        rp_obj = self.pool.get(model)
        if action == 'create':     
            #TODO: CREATE
            endpoint_sufix = rp_obj.get_odoo_url(cursor, uid, openerp_id, context=context)
            odoo_id, erp_id = self.exist(cursor, uid, model, endpoint_sufix)
            if odoo_id:
                self.update_odoo_id(cursor, uid, model, openerp_id, odoo_id, context=context)
                if not erp_id:
                    self.update_erp_id(cursor, uid, model, odoo_id, openerp_id, context=context)
            else:
                if MAPPING_MODELS_POST.get(model, False):
                    data = {}
                    if 'country_id' in vals and 'country_id' in rp_obj.FIELDS_FK:
                        odoo_id, erp_id = self.exist(cursor, uid, 'res.country', 'ES')
                        if odoo_id:
                            data['country_id'] = odoo_id
                        #TODO: que fem si no existeix?

                    url_base = odoo_url_api + MAPPING_MODELS_POST.get(model)
                    headers = {
                        "X-API-Key": odoo_api_key,
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    }
                    data.update({
                        "name": vals['name'],
                        "code": vals['ree_code'],
                        "pnt_erp_id": openerp_id,
                    })
                    response = requests.post(url_base, json=data, headers=headers)
                    if response.status_code == 201:
                        data = response.json()
                        if data and 'success' in data and data['success'] == True:
                            odoo_id = data['data']['odoo_id']
                            if odoo_id:
                                self.update_odoo_id(cursor, uid, model, openerp_id, odoo_id, context=context)
                    else:
                        print("ERROR CREATING IN ODOO:", response.status_code, response.text)
                else:
                    print("NO CREATE SUPPORTED IN ODOO FOR MODEL:", model)

        elif action == 'write':
            #TODO: WRITE
            print("WRITE SYNC TOODO")
        elif action == 'unlink':
            #TODO: UNLINK
            print("UNLINK SYNC TOODO")

        return True

    def exist(self, cursor, uid, model, url_sufix, context={}):
        odoo_url_api, odoo_api_key = self._get_conn_params(cursor, uid)
        url_base = odoo_url_api + MAPPING_MODELS_GET.get(model) + "/" + url_sufix
        headers = {
            "X-API-Key": odoo_api_key,
            "Accept": "application/json",
        }
        response = requests.get(url_base, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data and 'success' in data and data['success'] == True:
                return data['data']['odoo_id'], data['data']['erp_id']
        return False, False

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

    def update_erp_id(self, cursor, uid, model, odoo_id, erp_id, context={}):
        odoo_url_api, odoo_api_key = self._get_conn_params(cursor, uid)
        url_base = "{}entity/{}/{}/{}".format(
            odoo_url_api, MAPPING_MODELS_ENTITIES.get(model), odoo_id, erp_id
        )
        headers = {
            "X-API-Key": odoo_api_key,
            "Accept": "application/json",
        }
        response = requests.patch(url_base, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data and 'success' in data and data['success'] == True:
                return True
        return False

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
