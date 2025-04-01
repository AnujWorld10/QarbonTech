from typing import List

from pydantic import Field
from src.schemas.qcl_cc_schemas.cross_connect_order_schema import QclObject

from .common_schemas import MEFProductOrderItem_Common, ProductOrder_Common


class MEFProductOrderItem_Create(MEFProductOrderItem_Common):
    """
        An identified part of the order. A product order is decomposed into
        one or more order items. 
        The modelling pattern introduces the `Common` supertype to
        aggregate attributes that are common to both `ProductOrderItem` and
        `ProductOrderItem_Create`. The `Create` type has a subset of
        attributes of the response type and does not introduce any new,
        thus the `Create` type has an empty definition.
    """

class ProductOrder_Create(ProductOrder_Common, QclObject):
    """
        A Product Order is a type of order which  can  be used to place an
        order between a customer and a service provider or between a
        service provider and a partner and vice versa, Skipped properties:
        id,href,completionDate,orderDate,state,stateChange,cancellationDate,cancellationReason
    """
    productOrderItem: List[MEFProductOrderItem_Create] = Field(
        min_items=1,
        description="Items contained in the Product Order."
    )

