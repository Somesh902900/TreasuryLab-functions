import pymysql

def process_trade(db_conn, bond_uid, buyer_id, seller_id, trade_price, quantity):
    """
    Processes a trade, updating weighted average price (WAP) for the buyer
    and realized P&L for the seller.
    """
    try:
        with db_conn.cursor() as cursor:
            cursor.execute("""
                SELECT avg_buy_price FROM user WHERE user_uid = %s
            """, (buyer_id,))
            buyer_data = cursor.fetchone()
            buyer_avg_price = buyer_data[0] if buyer_data else 0

            cursor.execute("""
                SELECT COALESCE(SUM(quantity), 0) FROM tradebook
                WHERE buyer_id = %s AND bond_uid = %s
            """, (buyer_id, bond_uid))
            buyer_old_quantity = cursor.fetchone()[0]

            if buyer_old_quantity == 0:
                new_buyer_avg_price = trade_price
            else:
                new_buyer_avg_price = ((buyer_avg_price * buyer_old_quantity) + (trade_price * quantity)) / (buyer_old_quantity + quantity)

            cursor.execute("""
                UPDATE user SET avg_buy_price = %s WHERE user_uid = %s
            """, (new_buyer_avg_price, buyer_id))

            cursor.execute("""
                SELECT avg_buy_price, bpnl FROM user WHERE user_uid = %s
            """, (seller_id,))
            seller_data = cursor.fetchone()
            seller_avg_price, seller_realized_pnl = seller_data if seller_data else (0, 0)

            sell_pnl = (trade_price - seller_avg_price) * quantity
            new_seller_realized_pnl = seller_realized_pnl + sell_pnl

            cursor.execute("""
                UPDATE user SET bpnl = %s WHERE user_uid = %s
            """, (new_seller_realized_pnl, seller_id))

            db_conn.commit()
            print(f"Trade Processed: Bond {bond_uid}, Buyer {buyer_id} (Avg Price: {new_buyer_avg_price}), Seller {seller_id} (Realized P&L: {sell_pnl})")

    except Exception as e:
        db_conn.rollback()
        print("Error processing trade:", e)

db_conn = pymysql.connect(
    host="localhost",
    user="root",
    password="password",
    database="bond_trading"
)





