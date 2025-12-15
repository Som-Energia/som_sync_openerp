from osv import osv

MAPPING_MODELS_GET = {
    'res.country.state': 'states',
}
MAPPING_MODELS_POST = {
    'res.country.state': 'state',
}

class OdooSync(osv.osv_memory):
    "Sync manager"

    _name = "odoo.sync"
    _description = 'Syncronization manager'

    def _get_conn_params(self):
        imd_obj = self.pool.get('ir.model.data')
        try:
            odoo_url_api = imd_obj.get_object_reference(self._cr, self._uid,
                                    'som_sync_openerp', 'odoo_url_api')[1]
            odoo_api_key = imd_obj.get_object_reference(self._cr, self._uid,
                                    'som_sync_openerp', 'odoo_api_key')[1]
        except Exception as e:
            raise osv.except_osv('Configuration error',
                                    'Odoo connection parameters not found.')
        return odoo_url_api, odoo_api_key

    @job(queue='sync_odoo')
    def syncronize(self, cursor, uid, model, action, openerp_ids, vals, context={}, check=True, update_check=True):
        odoo_url_api, odoo_api_key = self._get_conn_params()
        if isinstance(openerp_ids, list):
            openerp_ids = openerp_ids[0]

        rp_obj = self.pool.get(model)
        if action == 'create':     
            #TODO: CREATE
            url = odoo_url_api + MAPPING_MODELS_POST.get(model)
            

        elif action == 'write':
            #TODO: WRITE
        elif action == 'unlink':
            #TODO: UNLINK



OdooSync()
