from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OriginalItemDetails(BaseModel):
    ccCancelReason : str

class QclItemDetails(BaseModel):
    inventoryItemName : str = "Cross Connect"
    #ccCancelDetails   : OriginalItemDetails #= Field(default={}) #dict or list[str] as per QCL schema docs.
    originalItemDetails : list[str] = Field(default=[])

class SourceFields(BaseModel):
    iaId : str
    itemDetails: List[QclItemDetails]
    

class GenericFields(BaseModel):
    pass

class DestinationFields(BaseModel):
    pass

class QclTransactionDataObject(BaseModel):
    genericFields: GenericFields = Field(default={})
    sourceFields: SourceFields
    destinationFields: DestinationFields = Field(default={})

class QclObject(BaseModel):
    # qcl_generic_data: QclGenericDataObject
    transactionData: QclTransactionDataObject
