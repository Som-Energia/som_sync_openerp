# som_sync

An OpenERP module to syncronize OpenERP with Odoo

[![SOM_MODULES](https://github.com/Som-Energia/openerp_som_addons/actions/workflows/som_sync_openerp.yml/badge.svg)](https://github.com/Som-Energia/openerp_som_addons/actions/workflows/som_sync_openerp.yml) [![codecov](https://codecov.io/github/Som-Energia/som_sync_openerp_modules/graph/badge.svg?token=VO8F4EIY8K)](https://codecov.io/github/Som-Energia/som_sync_openerp_modules)

## How to use

Add Odoo connection params in res.config of OpenERP

```
odoo_url_api
odoo_api_key
```

## What it does

*  This OpenERP module override methods create, write, unlink of modules ResPartner, AccountAccount, AccountJournal, AccountMove and AccountMoveLine.
*  Encueue whatever action it does, in a queue to update to Odoo asyncronious.
*  The worker try to create, write or unlink the object in Odoo.


## Odoo API doc
The API documentation is here https://som-energia.github.io/odoo_api_doc/index_swagger.html
