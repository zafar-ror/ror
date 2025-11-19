import frappe

@frappe.whitelist(allow_guest=True)
def get_noon_details():
    try:
        frappe.local.response["message"] = {
            "data": frappe.local.request
        }

    except Exception as e:
        frappe.local.response["message"] = {
            "data": e
        }
        err = "Error: {0}".format(e)
        return {"status": "error", "message": err}