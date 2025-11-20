import frappe

from frappe import _, bold

from erpnext.manufacturing.doctype.job_card.job_card import JobCard
from frappe.utils import (
	flt,
	get_link_to_form,
)


class CustomJobCard(JobCard):
	def validate_job_card(self):
		if self.work_order and frappe.get_cached_value("Work Order", self.work_order, "status") == "Stopped":
			frappe.throw(
				_("Transaction not allowed against stopped Work Order {0}").format(
					get_link_to_form("Work Order", self.work_order)
				)
			)

		if not self.time_logs:
			frappe.throw(
				_("Time logs are required for {0} {1}").format(
					bold("Job Card"), get_link_to_form("Job Card", self.name)
				)
			)
		elif frappe.db.get_single_value("Manufacturing Settings", "enforce_time_logs"):
			for row in self.time_logs:
				if not row.from_time or not row.to_time:
					frappe.throw(
						_("Row #{0}: From Time and To Time fields are required").format(row.idx),
					)

		precision = self.precision("total_completed_qty")
		total_completed_qty = flt(
			flt(self.total_completed_qty, precision) + flt(self.process_loss_qty, precision)
		)

		if self.for_quantity and flt(total_completed_qty, precision) != flt(self.for_quantity, precision):
			total_completed_qty_label = bold(_("Total Completed Qty"))
			qty_to_manufacture = bold(_("Qty to Manufacture"))

			frappe.msgprint(
				_("The {0} ({1}) must be equal to {2} ({3})").format(
					total_completed_qty_label,
					bold(flt(total_completed_qty, precision)),
					qty_to_manufacture,
					bold(self.for_quantity),
				)
			)
