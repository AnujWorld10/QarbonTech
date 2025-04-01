def check_sellerid_buyerId_present(json_result, buyerId, sellerId):
    seller_id = json_result.get("sellerId")
    buyer_id = json_result.get("buyerId")
    if sellerId == seller_id and buyerId == buyer_id:
        return True
    else:
        return False
def check_seller_id(json_result, sellerId):
    sellerid = json_result.get("sellerId")
    if sellerId == sellerid:
        return True
    else:
        return False
def check_buyer_id(json_result, buyerId):
    buyerid = json_result.get("buyerId")
    if buyerId == buyerid:
        return True
    else:
        return False
 
