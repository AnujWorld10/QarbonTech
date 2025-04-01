from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field
from src.schemas.qcl_cc_schemas.cross_connect_order_schema import (
    DestinationFields, GenericFields)


class QCLMoveType(str, Enum):
    A  = "a"
    AA = "A"
    Z  = "z"
    ZZ = "Z"

class QclCrossconnectMoveDetails(BaseModel):
    ccMoveType: QCLMoveType # Optional as per qcl schema
    ccPortId: str # Optional as per qcl schema
    ccId: str # Optional as per qcl schema
    ccLoaAttachmentId: str = Field(default="")
    ccMoveRequestDate: date # Optional as per qcl schema

class QclItemDetails(BaseModel):
    inventoryItemId: str
    inventoryItemName: str
    ccMoveDetails: QclCrossconnectMoveDetails # Optional as per qcl schema
    originalItemDetails: List[str] = Field(default=[])

class SourceOrderFields(BaseModel):
    iaId: str
    itemDetails: List[QclItemDetails]

class SourceFields(SourceOrderFields):
    pass

class QclTransactionDataObject(BaseModel):
    genericFields: GenericFields = Field(default={}) # Required as per qcl schema
    sourceFields: SourceFields
    destinationFields: DestinationFields = Field(default={}) 

class NorthEntity(str, Enum):
    ZOH = "ZOH"
    ONS = "ONS"
    SLF = "SLF"

class SouthEntity(str, Enum):
    EQX = "EQX"
    CYX = "CYX"

class QclGenericDataObject(BaseModel):
    sourceId: NorthEntity
    destinationId: SouthEntity

class QclCrossConnectMoveObject(BaseModel):
    genericData: QclGenericDataObject
    transactionData: QclTransactionDataObject