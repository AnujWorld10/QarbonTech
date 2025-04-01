from pydantic import BaseModel, Field
from typing import Optional

class AdditionalDetails(BaseModel):
    cabinetNumber: Optional[str] = Field(default = "")
    customerOrCarrierCircuitID: Optional[str] = Field(default = "")
    finalzSideSystemName: Optional[str] = Field(default = "")
    productBundle: Optional[str] = Field(default = "")
    patchPanelNumber: Optional[str] = Field(default = "")

class QclEQXListResponse(BaseModel):
    assetNumber: Optional[str] = Field(default = "")
    serialNumber: Optional[str] = Field(default = "")
    orderNumber: Optional[str] = Field(default = "")
    productName: Optional[str] = Field(default = "")
    ibx: Optional[str] = Field(default = "")
    cage: Optional[str] = Field(default = "")
    productDescription: Optional[str] = Field(default = "")
    accountNumber: Optional[str] = Field(default = "")
    relatedAccountNumber: Optional[str] = Field(default = "")
    accountName: Optional[str] = Field(default = "")
    installationDate: Optional[str] = Field(default = "")
    customerReferenceNumber: Optional[str] = Field(default = "")
    billingAgreementNumber: Optional[str] = Field(default = "")
    status: Optional[str] = Field(default = "")
    additionalDetails: AdditionalDetails = Field(default = "")
    
    
class TypeObjData(BaseModel):
    id: Optional[int] = Field(default = "")
    name: Optional[str] = "Cross Connect"
    
class StatusObjData(BaseModel):
    id: Optional[int] = Field(default = "")
    name: Optional[str] = Field(default = "")
    
class AccountObjData(BaseModel):
    id: Optional[str] = Field(default = "")
    name: Optional[str] = Field(default = "")
    alias : Optional[str] = Field(default = "")
    type : Optional[TypeObjData] = Field(default = "")
    bpId : Optional[str] = Field(default = "")
    ban : Optional[str] = Field(default = "")
    
class LocationDataObj(BaseModel):
    metro : Optional[str] = Field(default = "")
    
class DataCenterDataObj(BaseModel):
    id : Optional[str] = Field(default = "")
    name : Optional[str] = Field(default = "")
    isActive : Optional[bool] = Field(default=False)
    isThirdParty : Optional[bool] = Field(default=False)
    location : Optional[LocationDataObj] = Field(default = "")
    
    
class PodDataObj(BaseModel):
    id : Optional[str] = Field(default = "")
    name : Optional[str] = Field(default = "")
    shortName : Optional[str] = Field(default = "")
    alias :Optional[str] = Field(default = "")
    
    
class TypeRackDataObj(BaseModel):
    name : Optional[str] = Field(default = "")
    
class RackDataObj(BaseModel):
    id : Optional[str] = Field(default = "")
    name : Optional[str] = Field(default = "")
    serviceId: Optional[str] = Field(default = "")
    shortName : Optional[str] = Field(default = "")
    alias : Optional[str] = Field(default = "")
    type : Optional[TypeRackDataObj] = Field(default = "")
    
class AportDataObj(BaseModel):
    id : Optional[str] = Field(default = "")
    name : Optional[str] = Field(default = "")
    
class EcosystemConnectBundleDataObj(BaseModel):
    id : Optional[str] = Field(default = "")
    name : Optional[str] = Field(default = "")
    shortName : Optional[str] = Field(default = "")
    alias : Optional[str] = Field(default = "")
    cableType : Optional[str] = Field(default = "")
    serviceId: Optional[str] = Field(default = "")
    mediaType : Optional[str] = Field(default = "")
    dataCenter : Optional[DataCenterDataObj] = Field(default = "")
    
class EcosystemDataObj(BaseModel):
    ecosystemConnectBundle : Optional[EcosystemConnectBundleDataObj] = Field(default = "")
    type : Optional[TypeObjData] = Field(default = "") 
    
class QclCYXListResponse(BaseModel):
    id: Optional[str] = Field(default = "")
    name: Optional[str] = Field(default = "")
    serviceId: Optional[str] = Field(default = "")
    type : Optional[TypeObjData] = Field(default = "")
    status : Optional[StatusObjData] = Field(default = "")
    isThirdParty : Optional[bool] = Field(default=False)
    account : Optional[AccountObjData] = Field(default = "")
    shortName : Optional[str] = Field(default = "")
    alias : Optional[str] = Field(default = "")
    ZEndConnectingParty : Optional[str] = Field(default = "")
    ZEndConnectingPartyReferenceId : Optional[str] = Field(default = "")
    otherCustomerProvider : Optional[str] = Field(default = "")
    otherCustomerProviderReferenceId : Optional[str] = Field(default = "")
    crossConnectType : Optional[str] = Field(default = "")
    dataCenter  : Optional[DataCenterDataObj] = Field(default = "")
    pod : Optional[PodDataObj] = Field(default = "")
    rack : Optional[RackDataObj] = Field(default = "")
    aPort : Optional[AportDataObj] = Field(default = "")
    ecosystem : Optional[EcosystemDataObj] = Field(default = "")









