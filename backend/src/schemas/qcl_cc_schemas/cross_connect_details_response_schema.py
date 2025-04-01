
from typing import List, Optional
from pydantic import BaseModel,Field,HttpUrl, StrictInt
from datetime import datetime
from enum import Enum
from typing import List, Optional

class productDetailsObj(BaseModel):
    key : Optional[str] = Field(default = None)
    value : Optional[str] = Field(default = None)
    tag   : Optional[str] = Field(default = None)


class QclEqunixDetailsResponse(BaseModel):
    assetNumber : Optional[str] = Field(default = None)
    serialNumber : Optional[str] = Field(default = None)
    orderNumber : Optional[str] = Field(default = None)
    productName : Optional[str] = Field(default = None)
    ibx  : Optional[str] = Field(default = None)
    cage : Optional[str] = Field(default = None)
    productDescription : Optional[str] = Field(default = None)
    accountNumber : Optional[str] = Field(default = None)
    accountName : Optional[str] = Field(default = None)
    installationDate : Optional[str] = Field(default = None)
    customerReferenceNumber : Optional[str] = Field(default = None)
    status : Optional[str] = Field(default = None)
    productDetails : Optional[List[productDetailsObj]] = Field(default = None)
    
    

class NorthEntity(str,Enum):
    """Enumeration of North Entities."""

    ONS = "ONS"
    ZOH = "ZOH"
    
class SouthEntity(str,Enum):
    EQX = "EQX"
    CYX = "CYX"
    
class QclGenericDataObject(BaseModel):
    qcl_source_id    : NorthEntity = Field(description="An identifier indicating the source(north) from which the transaction originated.Ex:ONS for Net Suite and ZOH for Zoho")
    qcl_destination_id : SouthEntity = Field(description="An identifier indicating the destination to which the transaction is directed(south). Ex: EQX for Equinix and CYX for Cyxtera")

class QclTransactionDataObject(BaseModel):
    generic_fields       : Optional[dict] = Field(description="A dictionary containing generic fields associated with the item details.")
    source_fields        : dict   = Field(description="A dictionary containing data specific to the source specific fields of the transaction.")
    destination_fields   : Optional[dict] = Field(description="Fields containing information specific to the destination(south) of the transaction, if applicable.")
       

class CrossConnect_list(BaseModel):
    qcl_generic_data : QclGenericDataObject = Field(description="These are the common fields which are not specific to source or destination. E.g. time_initiated, lattice_username, etc.")
    qcl_transaction_data : QclTransactionDataObject =  Field(description="Data specific to a transaction in the Lattice")

class SourceDetailsFields(BaseModel):
    qcl_cc_id: str = Field(description="id of the cross connect details you want to fetch")


class QclTransactionDetailsDataObject(BaseModel):
    generic_fields       : Optional[dict] = Field(description="A dictionary containing generic fields associated with the item details.")
    source_fields        : SourceDetailsFields   = Field(description="A dictionary containing data specific to the source specific fields of the transaction.")
    destination_fields   : Optional[dict] = Field(description="Fields containing information specific to the destination(south) of the transaction, if applicable.")
     


class CrossConnect_details(BaseModel):
    qcl_generic_data : QclGenericDataObject = Field(description="These are the common fields which are not specific to source or destination. E.g. time_initiated, lattice_username, etc.")
    qcl_transaction_data : QclTransactionDetailsDataObject =  Field(description="Data specific to a transaction in the Lattice")

class StatusDataObject(BaseModel):
    id : Optional[int] = Field(default = None)
    name : Optional[str] = Field(default = None)
    
class AccountTypeDataObject(BaseModel):
    id : Optional[int] = Field(default = None)
    name : Optional[str] = Field(default = None)
    
class AccountDataObject(BaseModel):
    id : Optional[str] = Field(default = None)
    name : Optional[str] = Field(default = None)
    alias : Optional[str] = Field(default = None)
    type : Optional[AccountTypeDataObject] = Field(default = None)
    bpId : Optional[str]   = Field(default = None)
    ban  : Optional[str]   = Field(default = None)
    

class LocationDataObject(BaseModel):
    metro : Optional[str] = Field(default = None)
    
    
class DataCenterDataObject(BaseModel):
    id : Optional[str] = Field(default = None)
    name : Optional[str] = Field(default = None)   
    isActive : bool = Field(default=False)
    isThirdParty : bool = Field(default=False)
    location   : Optional[LocationDataObject] = Field(default = None) 
    
    
class PodDataObject(BaseModel):
    id      :  Optional[str] = Field(default = None)
    name     :  Optional[str] = Field(default = None)
    shortName : Optional[str] = Field(default = None)
    alias     : Optional[str] = Field(default = None)
    
    
class RackTypeDataObject(BaseModel):
    name : Optional[str] = Field(default = None)
    

class RackDataObject(BaseModel):
    id :  Optional[str] = Field(default = None)
    name : Optional[str] = Field(default = None)
    serviceId : Optional[str] = Field(default = None)
    shortName   : Optional[str] = Field(default = None)
    alias     : Optional[str] = Field(default = None) 
    type      : Optional[RackTypeDataObject] = Field(default = None)

class APortDataObject(BaseModel):
    id :  Optional[str] = Field(default = None)
    name : Optional[str] = Field(default = None)
    
class EcoSystemConnectBundleDataObject(BaseModel):
    id     :    Optional[str] = Field(default = None)
    name   :    Optional[str] = Field(default = None)
    shortName   : Optional[str] = Field(default = None)
    alias     : Optional[str] = Field(default = None)
    cableType : Optional[str] = Field(default = None)
    serviceId : Optional[str] = Field(default = None)
    mediaType : Optional[str] = Field(default = None)
    dataCenter  : Optional[DataCenterDataObject] = Field(default = None)
    
    
class EcoSystemDataObject(BaseModel):
    ecosystemConnectBundle : Optional[EcoSystemConnectBundleDataObject] = Field(default = None)
    type : Optional[AccountTypeDataObject] = Field(default = None)
        
    
class CrossConnectCYXDetailsResponse(BaseModel):
    id :  Optional[str] = Field(default = None)
    name : Optional[str] = Field(default = None)
    serviceId : Optional[str] = Field(default = None)
    status    : StatusDataObject = Field(default = None)
    isThirdParty : bool = Field(default=False)
    account      : Optional[AccountDataObject] = Field(default = None)
    shortName   : Optional[str] = Field(default = None)
    alias     : Optional[str] = Field(default = None)
    legacyName : Optional[str] = Field(default = None)
    ZEndConnectingParty : Optional[str] = Field(default = None)
    ZEndConnectingPartyReferenceId : Optional[str] = Field(default = None)
    otherCustomerProvider : Optional[str] = Field(default = None)
    otherCustomerProviderReferenceId : Optional[str] = Field(default = None)
    crossConnectType : Optional[str] = Field(default = None)
    dataCenter  : Optional[DataCenterDataObject] = Field(default = None)
    pod       :  Optional[PodDataObject] = Field(default = None)
    rack   : Optional[RackDataObject] = Field(default = None)
    aPort  : Optional[APortDataObject] = Field(default = None)
    ecosystem : Optional[EcoSystemDataObject] = Field(default = None)
    
class RackDetailsDataObject(BaseModel):
    id :  Optional[str] = Field(default = None)
    name : Optional[str] = Field(default = None)
    serviceId : Optional[str] = Field(default = None)
    shortName   : Optional[str] = Field(default = None)
    alias     : Optional[str] = Field(default = None) 
    status    : Optional[StatusDataObject] = Field(default = None)
    type      : Optional[RackTypeDataObject] = Field(default = None)
    
class CrossConnectCYXListResponse(BaseModel):
    id :  Optional[str] = Field(default = None)
    name : Optional[str] = Field(default = None)
    serviceId : Optional[str] = Field(default = None)
    type : Optional[AccountTypeDataObject] = Field(default = None)
    status    : Optional[StatusDataObject] = Field(default = None)
    isThirdParty : bool = Field(default = False)
    account      : Optional[AccountDataObject] = Field(default = None)
    shortName   : Optional[str] = Field(default = None)
    alias     : Optional[str] = Field(default = None)
    legacyName : Optional[str] = Field(default = None)
    ZEndConnectingParty : Optional[str] = Field(default = None)
    ZEndConnectingPartyReferenceId : Optional[str] = Field(default = None)
    otherCustomerProvider : Optional[str] = Field(default = None)
    otherCustomerProviderReferenceId : Optional[str] = Field(default = None)
    crossConnectType : Optional[str] = Field(default = None)
    dataCenter  : Optional[DataCenterDataObject] = Field(default = None)
    pod       :  Optional[PodDataObject] = Field(default = None)
    rack   : Optional[RackDetailsDataObject] = Field(default = None)
    aPort  : Optional[APortDataObject] = Field(default = None)
    ecosystem : Optional[EcoSystemDataObject] = Field(default = None)
    
    
    
    