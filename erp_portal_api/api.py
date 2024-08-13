import frappe
import json
import requests

@frappe.whitelist()
def create_delivery_note():
    data = json.loads(frappe.request.data)

    doc = frappe.new_doc("Delivery Note")
    doc.customer = data["customer"]
    doc.set_posting_time = 1
    doc.posting_date = data["posting_date"]
    doc.po_no = data["po_no"]
    doc.dn_no = data["dn_no"]
    doc.vehicle_no = data["vehicle_no"]
    doc.selling_price_list = "Standard Selling"
    sales_order = frappe.get_value("Sales Order", {"po_no": data["po_no"]}, ["name"])
    if not sales_order:
        return {"status":"404", "message":f"Tidak terdapat Sales Order dengan Customer Purchase Order {data['po_no']}"}
    customer_po_date = frappe.get_value("Sales Order", {"po_no": data["po_no"]}, ["po_date"])
    set_warehouse = frappe.get_value("Sales Order", {"po_no": data["po_no"]}, ["set_warehouse"])
    doc.set_warehouse = set_warehouse
    doc.po_date = customer_po_date
    for item in data["items"]:
        so_detail = frappe.get_value("Sales Order Item", {"parent": sales_order, "item_code": item["item_code"]}, ["name"])
        item["against_sales_order"] = sales_order
        
        if so_detail:
            item["so_detail"] = so_detail
        else:
            return {"status":"404", "message":f"Tidak terdapat Item {item['item_code']} pada Sales Order {sales_order}"}
        doc.append("items", item)
    doc.insert()
    doc.save()
    return {"status":"200", "message":"Delivery Note ERP berhasil dibuat"}