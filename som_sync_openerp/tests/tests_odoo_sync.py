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

    def test___create_sync_record__ok(self):
        partner_id = self.imd_obj.get_object_reference(
            self.cursor, self.uid, 'base', 'res_partner_thymbra'
        )[1]
        context = {
            'sync_state': 'synced',
            'update_odoo_created_sync': True,
        }

        sync_id = self.os_obj._create_sync_record(
            self.cursor, self.uid, 'res.partner', partner_id, 5001, '2024-06-10 12:00:00', context
        )

        sync_record = self.os_obj.browse(self.cursor, self.uid, sync_id)
        self.assertEqual(sync_record.model.model, 'res.partner')
        self.assertEqual(sync_record.res_id, partner_id)
        self.assertEqual(sync_record.odoo_id, 5001)
        self.assertEqual(sync_record.sync_state, 'synced')

    def test___create_sync_record__error(self):
        partner_id = self.imd_obj.get_object_reference(
            self.cursor, self.uid, 'base', 'res_partner_thymbra'
        )[1]
        context = {
            'sync_state': 'error',
            'odoo_last_update_result': '{"message": "err", "error_code": "INTERNAL_SERVER_ERROR"}',
            'update_last_sync': True,
        }

        sync_id = self.os_obj._create_sync_record(
            self.cursor, self.uid, 'res.partner', partner_id, 0, '2024-06-10 12:00:00', context
        )

        sync_record = self.os_obj.browse(self.cursor, self.uid, sync_id)
        self.assertEqual(sync_record.model.model, 'res.partner')
        self.assertEqual(sync_record.res_id, partner_id)
        self.assertEqual(sync_record.odoo_id, 0)
        self.assertEqual(sync_record.sync_state, 'error')

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
