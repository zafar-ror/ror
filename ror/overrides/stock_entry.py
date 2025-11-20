import frappe

from frappe import _
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry

from frappe.utils import (
	flt,
	get_link_to_form,
)

class CustomStockEntry(StockEntry):
	def check_if_operations_completed(self):
		"""Check if Time Sheets are completed against before manufacturing to capture operating costs."""
		prod_order = frappe.get_doc("Work Order", self.work_order)
		allowance_percentage = flt(
			frappe.db.get_single_value("Manufacturing Settings", "overproduction_percentage_for_work_order")
		)

		for d in prod_order.get("operations"):
			total_completed_qty = flt(self.fg_completed_qty) + flt(prod_order.produced_qty)
			completed_qty = (
				d.completed_qty + d.process_loss_qty + (allowance_percentage / 100 * d.completed_qty)
			)
			if flt(total_completed_qty, self.precision("fg_completed_qty")) > flt(
				completed_qty, self.precision("fg_completed_qty")
			):
				job_card = frappe.db.get_value("Job Card", {"operation_id": d.name}, "name")
				if not job_card:
					frappe.throw(
						_("Work Order {0}: Job Card not found for the operation {1}").format(
							self.work_order, d.operation
						)
					)

				work_order_link = get_link_to_form("Work Order", self.work_order)
				job_card_link = get_link_to_form("Job Card", job_card)
				frappe.msgprint(
					_(
						"Row #{0}: Operation {1} is not completed for {2} qty of finished goods in Work Order {3}. Please update operation status via Job Card {4}."
					).format(
						d.idx,
						frappe.bold(d.operation),
						frappe.bold(total_completed_qty),
						work_order_link,
						job_card_link,
					)
				)
