# Copyright (C) 2024-TODAY Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestReservation(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.hotel_reserv_line_obj = self.env["hotel.reservation.line"]
        self.hotel_reserv_obj = self.env["hotel.reservation"]
        self.hotel_room_obj = self.env["hotel.room"]
        self.hotel_room_reserv_obj = self.env["hotel.room.reservation.line"]
        self.reserv_summary_obj = self.env["room.reservation.summary"]
        self.quick_room_reserv_obj = self.env["quick.room.reservation"]
        self.hotel_folio_obj = self.env["hotel.folio"]
        self.reserv_line = self.env.ref("hotel_reservation.hotel_reservation_0")
        self.room_type = self.env.ref("hotel.hotel_room_type_1")
        self.room = self.env.ref("hotel.hotel_room_0")
        self.company = self.env.ref("base.main_company")
        self.partner = self.env.ref("base.res_partner_2")
        self.pricelist = self.env.ref("product.list0")
        self.floor = self.env.ref("hotel.hotel_floor_ground0")
        self.manager = self.env.ref("base.user_root")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.price_list = self.env.ref("product.list0")
        cur_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.hotel_reserv_line = self.hotel_reserv_line_obj.create(
            {
                "name": "R/00001",
                "line_id": self.reserv_line.id,
                "reserve": [(6, 0, [self.room.id])],
                "categ_id": self.room_type.id,
            }
        )

        self.hotel_reserv = self.hotel_reserv_obj.create(
            {
                "reservation_no": "R/00002",
                "date_order": cur_date,
                "company_id": self.company.id,
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "checkin": cur_date,
                "checkout": cur_date,
                "adults": 1,
                "state": "draft",
                "children": 1,
                "partner_invoice_id": self.partner.id,
                "partner_order_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "reservation_line": [(6, 0, [self.room.id])],
            }
        )

        self.reserv_summary = self.reserv_summary_obj.create(
            {
                "name": "Room Reservation Summary",
                "date_from": cur_date,
                "date_to": cur_date,
            }
        )

        self.quick_room_reserv = self.quick_room_reserv_obj.create(
            {
                "partner_id": self.partner.id,
                "check_in": cur_date,
                "check_out": cur_date,
                "room_id": self.room.id,
                "company_id": self.company.id,
                "pricelist_id": self.pricelist.id,
                "partner_invoice_id": self.partner.id,
                "partner_order_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "adults": 1,
            }
        )

        self.hotel_room_reserv = self.hotel_room_reserv_obj.create(
            {
                "room_id": self.room.id,
                "check_in": cur_date,
                "check_out": cur_date,
            }
        )

        self.hotel_room = self.hotel_room_obj.create(
            {
                "product_id": self.room.product_id.id,
                "floor_id": self.floor.id,
                "max_adult": 2,
                "max_child": 1,
                "capacity": 4,
                "room_categ_id": self.room_type.categ_id.id,
                "status": "available",
                "product_manager": self.manager.id,
                "room_reservation_line_ids": [(6, 0, [self.hotel_room_reserv.id])],
            }
        )

        self.hotel_folio = self.hotel_folio_obj.create(
            {
                "name": "Folio/00003",
                "date_order": cur_date,
                "warehouse_id": self.warehouse.id,
                "invoice_status": "no",
                "pricelist_id": self.price_list.id,
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "state": "draft",
            }
        )

    def test_hotel_room_unlink(self):
        self.hotel_room.unlink()

    def test_cron_room_line(self):
        self.hotel_room.cron_room_line()

    def test_quick_room_reserv_on_change_check_out(self):
        self.quick_room_reserv._on_change_check_out()

    def test_quick_room_reserv_onchange_partner_id_res(self):
        self.quick_room_reserv._onchange_partner_id_res()

    def test_quick_room_reserv_default_get(self):
        fields = ["date_from", "room_id"]
        self.quick_room_reserv.default_get(fields)

    def test_default_get(self):
        fields = ["date_from", "date_to"]
        self.reserv_summary.default_get(fields)

    def test_room_reservation(self):
        self.reserv_summary.room_reservation()

    def test_get_room_summary(self):
        self.reserv_summary.get_room_summary()

    def test_check_reservation_rooms(self):
        for rec in self.hotel_reserv.reservation_line:
            self.assertEqual(len(rec.reserve), 1, "Please Select Rooms For Reservation")
        self.hotel_reserv._check_reservation_rooms()

    def test_unlink_reserv(self):
        self.assertEqual(self.hotel_reserv.state != "draft", False)
        self.hotel_reserv.unlink()

    def test_copy(self):
        self.hotel_reserv.copy()

    def test_reserv_check_in_out_dates(self):
        self.hotel_reserv.check_in_out_dates()

    def test_reserv_check_overlap(self):
        date1 = datetime.now()
        date2 = datetime.now() + timedelta(days=1)
        self.hotel_reserv.check_overlap(date1, date2)

    def test_onchange_partner_id(self):
        self.hotel_reserv._onchange_partner_id()

    def test_set_to_draft_reservation(self):
        self.hotel_reserv.set_to_draft_reservation()
        self.assertEqual(self.hotel_reserv.state == "draft", True)

    def test_send_reservation_maill(self):
        self.hotel_reserv.action_send_reservation_mail()

    def test_reservation_reminder_24hrs(self):
        self.hotel_reserv.reservation_reminder_24hrs()

    def test_create_folio(self):
        with self.assertRaises(ValidationError):
            self.hotel_reserv.create_folio()

    def test_onchange_check_dates(self):
        self.hotel_reserv._onchange_check_dates()

    def test_confirmed_reservation(self):
        self.hotel_reserv.confirmed_reservation()

    def test_cancel_reservation(self):
        self.hotel_reserv.cancel_reservation()
        self.assertEqual(self.hotel_reserv.state == "cancel", True)

    def test_write(self):
        self.hotel_folio.write({"reservation_id": self.hotel_reserv.id})

    def test_on_change_categ(self):
        self.hotel_reserv_line.on_change_categ()

    def test_unlink(self):
        self.hotel_reserv_line.unlink()
