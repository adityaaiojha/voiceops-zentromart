import os
import pandas as pd

DATA_DIR = "data"

def load_table(name: str):
    path = os.path.join(DATA_DIR, f"{name}.csv")
    if os.path.exists(path):
        return pd.read_csv(path, dtype=str)
    return pd.DataFrame()

def lookup_order(order_id: str, verification_input: str):
    """
    Looks up order details after verifying phone last 4 digits or delivery pincode.
    """
    orders_df = load_table("orders")
    customers_df = load_table("customers")
    
    if orders_df.empty or customers_df.empty:
        return {"success": False, "error": "Database files missing"}

    order_match = orders_df[orders_df["order_id"].str.upper() == order_id.upper()]
    if order_match.empty:
        return {"success": False, "error": f"Order {order_id} not found"}

    order_row = order_match.iloc[0]
    cust_id = order_row["customer_id"]
    delivery_pin = str(order_row.get("delivery_pincode", "")).strip()

    cust_match = customers_df[customers_df["customer_id"] == cust_id]
    phone = cust_match.iloc[0]["phone"] if not cust_match.empty else ""
    phone_last4 = str(phone)[-4:] if len(str(phone)) >= 4 else ""

    # Check verification gate
    verif = str(verification_input).strip()
    if verif not in [phone_last4, delivery_pin]:
        return {
            "verified": False,
            "error": "Verification failed. Last 4 digits of phone or pincode did not match."
        }

    return {
        "verified": True,
        "order_id": order_row["order_id"],
        "status": order_row.get("status", "Shipped"),
        "promised_date": order_row.get("promised_date", "2026-10-22"),
        "delivery_pincode": delivery_pin
    }

def create_ticket(summary: str, customer_id: str = "CUST1001", order_id: str = None):
    return {
        "created": True,
        "ticket_id": f"TICK-{abs(hash(summary)) % 100000}",
        "order_id": order_id,
        "summary": summary,
        "status": "Escalated to human support"
    }