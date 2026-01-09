# -*- coding: utf-8 -*-
from __future__ import absolute_import
from destral import testing
from som_sync_openerp.models.odoo_exceptions import (
    CreationNotSupportedException, ERPObjectNotExistsException
)


class TestOdooSync(testing.OOTestCaseWithCursor):

    def setUp(self):
        self.os_obj = self.openerp.pool.get("odoo.sync")
        self.imd_obj = self.openerp.pool.get("ir.model.data")
        super(TestOdooSync, self).setUp()

    def test_create_odoo_record__notSupported(self):
        with self.assertRaises(CreationNotSupportedException):
            self.os_obj.create_odoo_record(self.cursor, self.uid, 'res.municipi', {})

    def test_check_erp_record_exist__True(self):
        partner_id = self.imd_obj.get_object_reference(
            self.cursor, self.uid, 'base', 'res_partner_asus'
        )[1]

        res = self.os_obj.check_erp_record_exist(self.cursor, self.uid, 'res.partner', partner_id)

        self.assertEqual(res, True)

    def test_check_erp_record_exist__Exception(self):
        with self.assertRaises(ERPObjectNotExistsException):
            self.os_obj.check_erp_record_exist(self.cursor, self.uid, 'res.partner', 123456)

    def test__build_update_vals__syncPartnerAlreadySyncred__ok(self):
        sync_id = self.imd_obj.get_object_reference(
            self.cursor, self.uid, 'som_sync_openerp', 'odoo_partner_already_syncred'
        )[1]
        context = {
            'sync_state': 'synced',
            'update_last_sync': True,
        }

        vals, update = self.os_obj._build_update_vals(
            self.cursor, self.uid, sync_id, 1001, '2024-06-10 12:00:00', context
        )

        expected_vals = {
            'odoo_id': 1001,
            'odoo_last_sync_at': '2024-06-10 12:00:00',
            'sync_state': 'synced'
        }
        self.assertEqual(vals, expected_vals)
        self.assertEqual(update, False)

    def test__build_update_vals__syncPartnerAlreadySyncred__withError(self):
        sync_id = self.imd_obj.get_object_reference(
            self.cursor, self.uid, 'som_sync_openerp', 'odoo_partner_already_syncred'
        )[1]
        context = {
            'sync_state': 'error',
            'odoo_last_update_result': '{"message": "err", "error_code": "INTERNAL_SERVER_ERROR"}',
            'update_last_sync': True,
        }

        vals, update = self.os_obj._build_update_vals(
            self.cursor, self.uid, sync_id, 1001, '2024-06-10 12:00:00', context
        )

        expected_vals = {
            'odoo_id': 1001,
            'odoo_last_sync_at': '2024-06-10 12:00:00',
            'odoo_last_update_result': '{"message": "err", "error_code": "INTERNAL_SERVER_ERROR"}',
            'sync_state': 'error'
        }
        self.assertEqual(vals, expected_vals)
        self.assertEqual(update, True)

    def test__build_update_vals__syncCountryStateError_withOk(self):
        sync_id = self.imd_obj.get_object_reference(
            self.cursor, self.uid, 'som_sync_openerp', 'odoo_country_state_error'
        )[1]
        context = {
            'sync_state': 'synced',
            'update_last_sync': True,
        }

        vals, update = self.os_obj._build_update_vals(
            self.cursor, self.uid, sync_id, 1001, '2024-06-10 12:00:00', context
        )

        expected_vals = {
            'odoo_id': 1001,
            'odoo_last_sync_at': '2024-06-10 12:00:00',
            'odoo_last_update_result': '',
            'sync_state': 'synced'
        }
        self.assertEqual(vals, expected_vals)
        self.assertEqual(update, False)
