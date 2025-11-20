import frappe

from erpnext.stock.doctype.item.item import Item


class CustomItem(Item):
    def update_item_price(self):
        frappe.db.sql(
			"""
				UPDATE `tabItem Price`
				SET
					item_description=%(item_description)s,
					brand=%(brand)s
				WHERE item_code=%(item_code)s
			""",
			dict(
				# item_name=self.item_name,
				item_description=self.description,
				brand=self.brand,
				item_code=self.name,
			),
		)