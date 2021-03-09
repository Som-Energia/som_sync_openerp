# som_sync

An OpenERP module to syncronize OpenERP with Odoo

## How to use

Add Odoo connection params in file.conf of OpenERP

```
#Odoo connection variables
odoo_host = todoo.somenergia.lan
odoo_dbname = odoo
odoo_user = admin
odoo_pwd = admin
odoo_port = 8069
```

## What it does

*  This OpenERP module override methods create, write, unlink of modules ResPartner, AccountAccount, AccountJournal, AccountMove and AccountMoveLine.
*  Encueue whatever action it does, in a queue to update to Odoo asyncronious.
*  The worker try to create, write or unlink the object in Odoo. You need the (Odoo module)[https://github.com/Som-Energia/som_sync_odoo] because add openerp_id key in Odoo models.

