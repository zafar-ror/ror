
import frappe
from erpnext.stock.doctype.pick_list.pick_list import get_available_item_locations_for_serial_and_batched_item,get_available_item_locations_for_serialized_item,get_available_item_locations_for_batched_item,get_available_item_locations_for_other_item

def custom_get_available_item_locations(
	item_code,
	from_warehouses,
	required_qty,
	company,
	ignore_validation=False,
	picked_item_details=None,
	consider_rejected_warehouses=False,
):
	locations = []
	has_serial_no = frappe.get_cached_value("Item", item_code, "has_serial_no")
	has_batch_no = frappe.get_cached_value("Item", item_code, "has_batch_no")

	if has_batch_no and has_serial_no:
		locations = get_available_item_locations_for_serial_and_batched_item(
			item_code,
			from_warehouses,
			required_qty,
			company,
			consider_rejected_warehouses=consider_rejected_warehouses,
		)
	elif has_serial_no:
		locations = get_available_item_locations_for_serialized_item(
			item_code,
			from_warehouses,
			company,
			consider_rejected_warehouses=consider_rejected_warehouses,
		)
	elif has_batch_no:
		locations = get_available_item_locations_for_batched_item(
			item_code,
			from_warehouses,
			consider_rejected_warehouses=consider_rejected_warehouses,
		)
	else:
		locations = get_available_item_locations_for_other_item(
			item_code,
			from_warehouses,
			company,
			consider_rejected_warehouses=consider_rejected_warehouses,
		)

	# if picked_item_details:
	# 	locations = filter_locations_by_picked_materials(locations, picked_item_details)

	if locations:
		locations = get_locations_based_on_required_qty(item_code, from_warehouses, locations, required_qty)

	# if not ignore_validation:
	# 	validate_picked_materials(item_code, required_qty, locations, picked_item_details)

	return locations


def get_locations_based_on_required_qty(item_code, from_warehouses, locations, required_qty):
	filtered_locations = []

	for location in locations: 
		if location.qty < required_qty:
			frappe.msgprint(f"Item Code: {item_code} - Insufficient stock. Short by {required_qty - location.qty} units in Warehouse: {from_warehouses[0]}.")
		if location.qty >= required_qty:
			location.qty = required_qty
			filtered_locations.append(location)
			break

		required_qty -= location.qty
		filtered_locations.append(location)

	return filtered_locations