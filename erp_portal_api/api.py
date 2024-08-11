import frappe
import json
import requests

@frappe.whitelist()
def create_delivery_note(json_data):
    if isinstance(json_data, str):
        data = json.loads(data)
    else:
        data = json_data

    doc = frappe.get_doc("Delivery Note", data)
    sales_order, customer_po_date, set_warehouse = frappe.get_value("Sales Order", {"po_no": data["po_no"]}, ["name", "po_date", "set_warehouse"])
    doc.set_warehouse = set_warehouse
    doc.po_date = customer_po_date
    for item in doc.items:
        so_detail = frappe.get_value("Sales Order Item", {"parent": sales_order, "item_code": item.item_code}, ["so_detail"])
        if sales_order:
            item.against_sales_order = sales_order
        else:
            return {"status":"404", "message":f"Tidak terdapat Sales Order dengan Customer Purchase Order {data["po_no"]}"}
        if so_detail:
            item.so_detail = so_detail
        else:
            return {"status":"404", "message":f"Tidak terdapat Item {item.item_code} pada Sales Order {sales_order}"}
    doc.insert()
    doc.save()
    return {"status":"200", "message":"Delivery Note ERP berhasil dibuat"}