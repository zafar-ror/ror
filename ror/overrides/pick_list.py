import frappe
from erpnext.stock.doctype.pick_list.pick_list import PickList


class CustomPickList(PickList):
    @frappe.whitelist()
	def set_item_locations(self, save=False):
        pass
# 		self.validate_for_qty()
# 		items = self.aggregate_item_qty()
# 		picked_items_details = self.get_picked_items_details(items)
# 		self.item_location_map = frappe._dict()

# 		from_warehouses = [self.parent_warehouse] if self.parent_warehouse else []
# 		if self.parent_warehouse:
# 			from_warehouses.extend(get_descendants_of("Warehouse", self.parent_warehouse))

# 		# Create replica before resetting, to handle empty table on update after submit.
# 		locations_replica = self.get("locations")

# 		# reset
# 		reset_rows = []
# 		for row in self.get("locations"):
# 			if not row.picked_qty:
# 				reset_rows.append(row)

# 		for row in reset_rows:
# 			self.remove(row)

# 		updated_locations = frappe._dict()
# 		len_idx = len(self.get("locations")) or 0
# 		for item_doc in items:
# 			item_code = item_doc.item_code

# 			self.item_location_map.setdefault(
# 				item_code,
# 				get_available_item_locations(
# 					item_code,
# 					from_warehouses,
# 					self.item_count_map.get(item_code),
# 					self.company,
# 					picked_item_details=picked_items_details.get(item_code),
# 					consider_rejected_warehouses=self.consider_rejected_warehouses,
# 				),
# 			)

# 			locations = get_items_with_location_and_quantity(item_doc, self.item_location_map, self.docstatus)

# 			item_doc.idx = None
# 			item_doc.name = None

# 			for row in locations:
# 				location = item_doc.as_dict()
# 				location.update(row)
# 				key = (
# 					location.item_code,
# 					location.warehouse,
# 					location.uom,
# 					location.batch_no,
# 					location.serial_no,
# 					location.sales_order_item or location.material_request_item,
# 				)

# 				if key not in updated_locations:
# 					updated_locations.setdefault(key, location)
# 				else:
# 					updated_locations[key].qty += location.qty
# 					updated_locations[key].stock_qty += location.stock_qty

# 		for location in updated_locations.values():
# 			if location.picked_qty > location.stock_qty:
# 				location.picked_qty = location.stock_qty

# 			len_idx += 1
# 			location.idx = len_idx
# 			self.append("locations", location)

# 		# If table is empty on update after submit, set stock_qty, picked_qty to 0 so that indicator is red
# 		# and give feedback to the user. This is to avoid empty Pick Lists.
# 		if not self.get("locations") and self.docstatus == 1:
# 			for location in locations_replica:
# 				location.stock_qty = 0
# 				location.picked_qty = 0

# 				len_idx += 1
# 				location.idx = len_idx
# 				self.append("locations", location)
# 			frappe.msgprint(
# 				_(
# 					"Please Restock Items and Update the Pick List to continue. To discontinue, cancel the Pick List."
# 				),
# 				title=_("Out of Stock"),
# 				indicator="red",
# 			)

# 		if save:
# 			self.save()

# def get_items_with_location_and_quantity(item_doc, item_location_map, docstatus):
# 	available_locations = item_location_map.get(item_doc.item_code)
# 	locations = []

# 	# if stock qty is zero on submitted entry, show positive remaining qty to recalculate in case of restock.
# 	remaining_stock_qty = item_doc.qty if (docstatus == 1 and item_doc.stock_qty == 0) else item_doc.stock_qty

# 	while flt(remaining_stock_qty) > 0 and available_locations:
# 		item_location = available_locations.pop(0)
# 		item_location = frappe._dict(item_location)

# 		stock_qty = remaining_stock_qty if item_location.qty >= remaining_stock_qty else item_location.qty
# 		qty = stock_qty / (item_doc.conversion_factor or 1)

# 		uom_must_be_whole_number = frappe.get_cached_value("UOM", item_doc.uom, "must_be_whole_number")
# 		if uom_must_be_whole_number:
# 			qty = floor(qty)
# 			stock_qty = qty * item_doc.conversion_factor
# 			if not stock_qty:
# 				break

# 		serial_nos = None
# 		if item_location.serial_no:
# 			serial_nos = "\n".join(item_location.serial_no[0 : cint(stock_qty)])

# 		locations.append(
# 			frappe._dict(
# 				{
# 					"qty": qty,
# 					"stock_qty": stock_qty,
# 					"warehouse": item_location.warehouse,
# 					"serial_no": serial_nos,
# 					"batch_no": item_location.batch_no,
# 				}
# 			)
# 		)

# 		remaining_stock_qty -= stock_qty

# 		qty_diff = item_location.qty - stock_qty
# 		# if extra quantity is available push current warehouse to available locations
# 		if qty_diff > 0:
# 			item_location.qty = qty_diff
# 			if item_location.serial_no:
# 				# set remaining serial numbers
# 				item_location.serial_no = item_location.serial_no[-int(qty_diff) :]
# 			available_locations = [item_location, *available_locations]

# 	# update available locations for the item
# 	item_location_map[item_doc.item_code] = available_locations
# 	return locations

# def get_available_item_locations(
# 	item_code,
# 	from_warehouses,
# 	required_qty,
# 	company,
# 	ignore_validation=True,
# 	picked_item_details=None,
# 	consider_rejected_warehouses=False,
# ):
# 	locations = []
# 	total_picked_qty = (
# 		sum([v.get("picked_qty") for k, v in picked_item_details.items()]) if picked_item_details else 0
# 	)
# 	has_serial_no = frappe.get_cached_value("Item", item_code, "has_serial_no")
# 	has_batch_no = frappe.get_cached_value("Item", item_code, "has_batch_no")

# 	if has_batch_no and has_serial_no:
# 		locations = get_available_item_locations_for_serial_and_batched_item(
# 			item_code,
# 			from_warehouses,
# 			required_qty,
# 			company,
# 			total_picked_qty,
# 			consider_rejected_warehouses=consider_rejected_warehouses,
# 		)
# 	elif has_serial_no:
# 		locations = get_available_item_locations_for_serialized_item(
# 			item_code,
# 			from_warehouses,
# 			required_qty,
# 			company,
# 			total_picked_qty,
# 			consider_rejected_warehouses=consider_rejected_warehouses,
# 		)
# 	elif has_batch_no:
# 		locations = get_available_item_locations_for_batched_item(
# 			item_code,
# 			from_warehouses,
# 			required_qty,
# 			company,
# 			total_picked_qty,
# 			consider_rejected_warehouses=consider_rejected_warehouses,
# 		)
# 	else:
# 		locations = get_available_item_locations_for_other_item(
# 			item_code,
# 			from_warehouses,
# 			required_qty,
# 			company,
# 			total_picked_qty,
# 			consider_rejected_warehouses=consider_rejected_warehouses,
# 		)

# 	total_qty_available = sum(location.get("qty") for location in locations)
# 	remaining_qty = required_qty - total_qty_available

# 	if remaining_qty > 0 and not ignore_validation:
# 		frappe.msgprint(
# 			_("{0} units of Item {1} is not available.").format(
# 				remaining_qty, frappe.get_desk_link("Item", item_code)
# 			),
# 			title=_("Insufficient Stock"),
# 		)

# 	if picked_item_details:
# 		for location in list(locations):
# 			key = (
# 				(location["warehouse"], location["batch_no"])
# 				if location.get("batch_no")
# 				else location["warehouse"]
# 			)

# 			if key in picked_item_details:
# 				picked_detail = picked_item_details[key]

# 				if picked_detail.get("serial_no") and location.get("serial_no"):
# 					location["serial_no"] = list(
# 						set(location["serial_no"]).difference(set(picked_detail["serial_no"]))
# 					)
# 					location["qty"] = len(location["serial_no"])
# 				else:
# 					location["qty"] -= picked_detail.get("picked_qty")

# 			if location["qty"] < 1:
# 				locations.remove(location)

# 		total_qty_available = sum(location.get("qty") for location in locations)
# 		remaining_qty = required_qty - total_qty_available

# 		if remaining_qty > 0 and not ignore_validation:
# 			frappe.msgprint(
# 				_("{0} units of Item {1} is picked in another Pick List.").format(
# 					remaining_qty, frappe.get_desk_link("Item", item_code)
# 				),
# 				title=_("Already Picked"),
# 			)

# 	return locations