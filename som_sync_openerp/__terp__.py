{
    "name" : "Syncronize OpenERP with Odoo",
    "version" : "0.1",
    "author" : "Som Energia SCCL",
    "website" : "https://github.com/Som-Energia/som_sync_openerp",
    "category" : "Added functionality",
    "depends" : ['base_extended_som'],
    "description": """Som Sync""",
    "demo_xml": [],
    "init_xml": [],
    "update_xml": [
        "data/som_sync_openerp_data.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
