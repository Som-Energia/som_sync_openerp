#  -*- coding: utf-8 -*-
from __future__ import absolute_import
from time import sleep
from osv import osv, fields
from oorq.decorators import job
import requests
from datetime import datetime
from .odoo_exceptions import CreationNotSupportedException
import logging

FF_ENABLE_ODOO_SYNC = True  # TODO: as variable in res.config ??

# Mapping of models: key -> erp model, value -> odoo endpoint sufix
MAPPING_MODELS_GET = {
    'res.country.state': 'state',
    'res.country': 'country',
    'res.municipi': 'city',
    'res.partner.bank': 'bank',
}

# Mapping of models entities to update erp_id in Odoo: key -> erp model, value -> odoo entity name
MAPPING_MODELS_ENTITIES = {
    'res.country.state': 'state',
    'res.country': 'country',
    'res.municipi': 'city',
    'res.partner.bank': 'bank',
}

# Mapping of models to post endpoint sufix: key -> erp model, value -> odoo endpoint sufix
MAPPING_MODELS_POST = {
    'res.country.state': 'states',
    'res.partner.bank': 'banks',
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
        except Exception:
            raise osv.except_osv('Configuration error',
                                 'Odoo connection parameters not found.')
        return odoo_url_api, odoo_api_key

    def _clean_context_update_dates(self, cursor, uid, context={}):
        res = context.copy()
        res.pop('update_last_sync', False)
        res.pop('update_odoo_created_sync', False)
        res.pop('update_odoo_updated_sync', False)
        return res

    def get_model_vals_to_sync(self, cursor, uid, model, id, context={}):
        rp_obj = self.pool.get(model)

        # Read fields that are not foreign keys
        keys_to_read = [key for key in rp_obj.MAPPING_FIELDS_TO_SYNC.keys()
                        if key not in rp_obj.MAPPING_FK.keys()]
        # TODO: check in prod if record id is already created when async
        data = rp_obj.read(cursor, uid, id, keys_to_read)

        # Read and sync foreign key fields
        keys_fk = [key for key in rp_obj.MAPPING_FIELDS_TO_SYNC.keys()
                   if key in rp_obj.MAPPING_FK.keys()]
        if keys_fk:
            context_copy = self._clean_context_update_dates(cursor, uid, context)
        for fk_field in keys_fk:
            model_fk = rp_obj.MAPPING_FK[fk_field]
            id_fk = rp_obj.read(cursor, uid, id, [fk_field])[fk_field][0]
            odoo_id, erp_id = self.syncronize_sync(
                cursor, uid, model_fk, 'sync', id_fk, context_copy)
            if not odoo_id:
                # TODO: handle missing foreign key
                print("FK NOT FOUND IN ODOO:", model_fk, id_fk)
            data[fk_field] = odoo_id

        # Map fields to sync
        result_data = {}
        for erp_key, odoo_key in rp_obj.MAPPING_FIELDS_TO_SYNC.items():
            if erp_key in data:
                result_data[odoo_key] = data[erp_key]
        return result_data

    def sync_model_enabled(self, cursor, uid, model):
        config_obj = self.pool.get('res.config')
        list_models_to_sync = eval(config_obj.get(cursor, uid, 'odoo_erp_models_to_sync', '[]'))
        if model in list_models_to_sync:
            return True
        return False

    @job(queue='sync_odoo', timeout=3600)
    def syncronize(self, cursor, uid,
                   model, action, openerp_id, context={},
                   check=True, update_check=True):
        context['update_last_sync'] = True
        self.syncronize_sync(cursor, uid, model, action, openerp_id,
                             context=context, check=check, update_check=update_check)

    def syncronize_sync(self, cursor, uid,
                        model, action, openerp_id, context={},
                        check=True, update_check=True):
        if not self.sync_model_enabled(cursor, uid, model):
            return False, False
        odoo_url_api, odoo_api_key = self._get_conn_params(cursor, uid)
        if isinstance(openerp_id, list):
            openerp_id = openerp_id[0]
        logger = logging.getLogger('openerp.odoo.sync')
        logger.info("Odoo syncronize {} with id {}".format(model, openerp_id))
        data = {}
        rp_obj = self.pool.get(model)
        try:
            max_attemps = 5
            attemp_n = 0
            while attemp_n < max_attemps:
                exists_erp_record = rp_obj.read(cursor, uid, openerp_id, ['name'])
                if not exists_erp_record:
                    print("ERP RECORD NOT FOUND:", model, openerp_id)
                    attemp_n += 1
                    sleep(5)
                else:
                    break
            if attemp_n == max_attemps:
                print("MAX ATTEMPS REACHED. SKIPPING SYNC FOR RECORD:", model, openerp_id)
                return False, False

            if action in ['create', 'sync']:
                data = self.get_model_vals_to_sync(
                    cursor, uid, model, openerp_id, context=context)

            elif action == 'write':
                # TODO: WRITE
                print("WRITE SYNC TOODO")
                context['sync_state'] = 'error'
            elif action == 'unlink':
                # TODO: UNLINK
                print("UNLINK SYNC TOODO")
                context['sync_state'] = 'error'

            # Get endpoint suffix for existence check
            endpoint_exists_suffix = rp_obj.get_endpoint_suffix(
                cursor, uid, openerp_id, context=context)

            # Check if exists in Odoo
            odoo_id, erp_id = self.exists(cursor, uid, model, endpoint_exists_suffix)

            if odoo_id:  # already exists in Odoo
                if not erp_id:
                    # update erp_id in Odoo
                    res = self.update_erp_id(
                        cursor, uid, model, odoo_id, openerp_id, context=context
                    )
                    if res:
                        erp_id = openerp_id
                        context['sync_state'] = 'synced'
                    else:
                        # TODO: when res is False?
                        print("ERROR UPDATING ERP_ID IN ODOO")
                        context['sync_state'] = 'error'
                else:
                    # TODO: Check if fields changed to update in Odoo?
                    context['sync_state'] = 'synced'

            else:  # not exists in Odoo, create it
                odoo_id, msg = self.create_odoo_record(
                    cursor, uid, model, data, context=context)
                if odoo_id:
                    # update odoo_id in OpenERP
                    context.update({
                        'update_odoo_created_sync': True,
                    })
                    erp_id = openerp_id
                    context['sync_state'] = 'synced'
                else:
                    print("ERROR CREATING RECORD IN ODOO FOR MODEL:", model)
                    context.update({
                        'odoo_last_update_result': msg,
                    })
                    context['sync_state'] = 'error'

        except CreationNotSupportedException as e:
            context['odoo_last_update_result'] = str(e)
            context['sync_state'] = 'error'
        finally:
            # update odoo_id in OpenERP
            self.update_odoo_id(cursor, uid, model, openerp_id, odoo_id, context=context)

        return odoo_id, erp_id

    def create_odoo_record(self, cursor, uid, model, data, context={}):
        odoo_url_api, odoo_api_key = self._get_conn_params(cursor, uid)
        post_sufix = MAPPING_MODELS_POST.get(model, False)
        if post_sufix:
            url_base = '{}{}'.format(odoo_url_api, MAPPING_MODELS_POST.get(model))
            headers = {
                "X-API-Key": odoo_api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            response = requests.post(url_base, json=data, headers=headers)
            if response.status_code == 201:
                data = response.json()
                if data and 'success' in data and data.get('success', False):
                    odoo_id = data['data']['odoo_id']
                    return odoo_id, ''
            else:
                print("ERROR CREATING IN ODOO:", response.status_code, response.text)
                return False, response.text
        else:
            raise CreationNotSupportedException(model)
        return False, ''

    def exists(self, cursor, uid, model, url_sufix, context={}):
        # mocked response for res.partner till implemented endpoint in Odoo
        if model == 'res.partner':
            odoo_id = 1617
            erp_id = 1
            return odoo_id, erp_id

        odoo_url_api, odoo_api_key = self._get_conn_params(cursor, uid)
        url_base = '{}{}/{}'.format(odoo_url_api, MAPPING_MODELS_GET.get(model), url_sufix)
        headers = {
            "X-API-Key": odoo_api_key,
            "Accept": "application/json",
        }
        response = requests.get(url_base, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data and 'success' in data and data.get('success', False):
                return data['data']['odoo_id'], data['data']['erp_id']
        return False, False

    def update_odoo_id(self, cursor, uid, model, openerp_id, odoo_id, context={}):
        ids = self.search(cursor, uid,
                          [('model.model', '=', model), ('res_id', '=', openerp_id)]
                          )
        str_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if not ids:
            vals = {
                'model': self.pool.get('ir.model').search(cursor, uid, [('model', '=', model)])[0],
                'res_id': openerp_id,
                'odoo_id': odoo_id,
                'odoo_last_sync_at': str_now,
            }
            if context.get('update_odoo_created_sync', False):
                vals['odoo_created_at'] = str_now
                vals['sync_state'] = 'synced'
            if context.get('odoo_last_update_result', False):
                vals['odoo_last_update_result'] = context.get('odoo_last_update_result')
                vals['sync_state'] = 'error'
            self.create(cursor, uid, vals)
            return True

        vals = {'odoo_id': odoo_id}
        if context.get('update_last_sync', False):
            vals['odoo_last_sync_at'] = str_now
            vals['sync_state'] = 'synced'
        if context.get('update_odoo_updated_sync', False):
            vals['odoo_updated_at'] = str_now
            vals['sync_state'] = 'synced'
        if context.get('odoo_last_update_result', False):
            vals['odoo_last_update_result'] = context.get('odoo_last_update_result')
            vals['sync_state'] = 'error'
        if context.get('sync_state', False):
            vals['sync_state'] = context.get('sync_state')

        if (context.get('update_last_sync')
            or context.get('update_odoo_updated_sync')
            or context.get('odoo_last_update_result', False)
                or context.get('sync_state', False)):
            self.write(cursor, uid, ids, vals, context=context)
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
            if data and 'success' in data and data.get('success', False):
                return True
        return False

    _columns = {
        'model': fields.many2one('ir.model', 'Model'),
        'res_id': fields.integer('ERP id'),
        'odoo_id': fields.integer('Odoo id'),
        # Aquest camp indica la última vegada que hem fet sync amb Odoo (s'hagin modificat o no les dades)  # noqa: E501
        'odoo_last_sync_at': fields.datetime('Odoo last sync at'),
        # Aquests camps indiquen la data de creacio i ultima modificacio al Odoo, no la data d'actualitzció de l'odoo_id a OpenERP  # noqa: E501
        'odoo_created_at': fields.datetime('Odoo created at'),
        'odoo_updated_at': fields.datetime('Odoo updated at'),
        # Resultat de la última actualització quan no han anat bé
        'odoo_last_update_result': fields.text('Odoo last update result'),
        'sync_state': fields.selection([
            ('synced', 'Synced'),
            ('pending', 'Pending'),
            ('error', 'Error'),
        ], 'Syncronization state', required=True),
    }

    _sql_constraints = [
        ('model_res_id_uniq', 'unique (model,res_id)', ("Model and res_id must be unique"))
    ]

    _defaults = {
        'sync_state': lambda obj, cr, uid, context: 'pending',
    }


OdooSync()
