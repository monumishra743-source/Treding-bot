
import json
from dhanhq import dhanhq

def place_dhan_order(client_id, access_token, action, symbol, quantity):
    """
    यह फ़ंक्शन धन API के जरिए असली मार्केट ऑर्डर प्लेस करता है।
    """
    try:
        if not access_token:
            return {"status": "error", "message": "एक्सेस टोकन गायब है!"}
        
        # धन API क्लाइंट को इनिशियलाइज करना
        dhan = dhanhq(client_id, access_token)
        
        # बाय या सेल तय करना
        transaction_type = dhan.BUY if action == "BUY" else dhan.SELL
        
        # कमोडिटी (MCX) आर्डर प्लेसमेंट लॉजिक
        # यदि आप सोमवार को शेयर्स में काम करें, तो dhan.MCX को बदलकर dhan.NSE कर सकते हैं
        order_response = dhan.place_order(
            tag="AlgoStarlight",
            transaction_type=transaction_type,
            exchange_segment=dhan.MCX, 
            product_type=dhan.INTRADAY, 
            order_type=dhan.MARKET,
            validity=dhan.DAY,
            security_id="25",  # नेचुरल गैस का डिफ़ॉल्ट आईडी
            quantity=int(quantity),
            price=0
        )
        
        return {"status": "success", "data": order_response}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
