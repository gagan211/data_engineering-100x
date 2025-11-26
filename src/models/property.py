"""Pydantic models for property data validation."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class ValuationRecord(BaseModel):
    """Valuation snapshot for a property."""
    list_price: Optional[float] = Field(None, alias="List_Price")
    previous_rent: Optional[float] = Field(None, alias="Previous_Rent")
    arv: Optional[float] = Field(None, alias="ARV")
    rent_zestimate: Optional[float] = Field(None, alias="Rent_Zestimate")
    low_fmr: Optional[float] = Field(None, alias="Low_FMR")
    high_fmr: Optional[float] = Field(None, alias="High_FMR")
    zestimate: Optional[float] = Field(None, alias="Zestimate")
    expected_rent: Optional[float] = Field(None, alias="Expected_Rent")
    redfin_value: Optional[float] = Field(None, alias="Redfin_Value")
    
    model_config = {"populate_by_name": True}


class HOARecord(BaseModel):
    """HOA fee information."""
    hoa_amount: Optional[float] = Field(None, alias="HOA")
    hoa_flag: Optional[str] = Field(None, alias="HOA_Flag")
    
    @field_validator("hoa_flag", mode="before")
    @classmethod
    def validate_flag(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v_upper = v.strip().upper()
            if v_upper not in ["YES", "NO"]:
                return None
            return v_upper
        return None
    
    model_config = {"populate_by_name": True}


class RehabRecord(BaseModel):
    """Rehab assessment and condition flags."""
    underwriting_rehab: Optional[float] = Field(None, alias="Underwriting_Rehab")
    rehab_calculation: Optional[float] = Field(None, alias="Rehab_Calculation")
    paint: Optional[str] = Field(None, alias="Paint")
    flooring_flag: Optional[str] = Field(None, alias="Flooring_Flag")
    foundation_flag: Optional[str] = Field(None, alias="Foundation_Flag")
    roof_flag: Optional[str] = Field(None, alias="Roof_Flag")
    hvac_flag: Optional[str] = Field(None, alias="HVAC_Flag")
    kitchen_flag: Optional[str] = Field(None, alias="Kitchen_Flag")
    bathroom_flag: Optional[str] = Field(None, alias="Bathroom_Flag")
    appliances_flag: Optional[str] = Field(None, alias="Appliances_Flag")
    windows_flag: Optional[str] = Field(None, alias="Windows_Flag")
    landscaping_flag: Optional[str] = Field(None, alias="Landscaping_Flag")
    trashout_flag: Optional[str] = Field(None, alias="Trashout_Flag")
    
    @field_validator(
        "flooring_flag", "foundation_flag", "roof_flag", "hvac_flag",
        "kitchen_flag", "bathroom_flag", "appliances_flag", "windows_flag",
        "landscaping_flag", "trashout_flag",
        mode="before"
    )
    @classmethod
    def normalize_flags(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v_upper = v.strip().upper()
            if v_upper not in ["YES", "NO"]:
                return None
            return v_upper
        return None
    
    model_config = {"populate_by_name": True}


class Property(BaseModel):
    """Core property entity with all denormalized data."""
    
    # Identifiers
    property_title: str = Field(..., alias="Property_Title")
    address: str = Field(..., alias="Address")
    
    # Location
    street_address: str = Field(..., alias="Street_Address")
    city: str = Field(..., alias="City")
    state: str = Field(..., alias="State")
    zip_code: str = Field(..., alias="Zip")
    latitude: float = Field(..., alias="Latitude")
    longitude: float = Field(..., alias="Longitude")
    
    # Characteristics
    property_type: str = Field(..., alias="Property_Type")
    year_built: Optional[int] = Field(None, alias="Year_Built")
    sqft_total: Optional[float] = Field(None, alias="SQFT_Total")
    sqft_basement: Optional[float] = Field(None, alias="SQFT_Basement")
    sqft_mu: Optional[float] = Field(None, alias="SQFT_MU")
    bed: Optional[int] = Field(None, alias="Bed")
    bath: Optional[int] = Field(None, alias="Bath")
    
    # Features
    layout: Optional[str] = Field(None, alias="Layout")
    pool: Optional[str] = Field(None, alias="Pool")
    parking: Optional[str] = Field(None, alias="Parking")
    basement_yes_no: Optional[str] = Field(None, alias="BasementYesNo")
    water: Optional[str] = Field(None, alias="Water")
    sewage: Optional[str] = Field(None, alias="Sewage")
    htw: Optional[str] = Field(None, alias="HTW")
    commercial: Optional[str] = Field(None, alias="Commercial")
    highway: Optional[str] = Field(None, alias="Highway")
    train: Optional[str] = Field(None, alias="Train")
    flood: Optional[str] = Field(None, alias="Flood")
    occupancy: Optional[str] = Field(None, alias="Occupancy")
    
    # Financial
    net_yield: Optional[float] = Field(None, alias="Net_Yield")
    irr: Optional[float] = Field(None, alias="IRR")
    taxes: Optional[float] = Field(None, alias="Taxes")
    tax_rate: Optional[float] = Field(None, alias="Tax_Rate")
    
    # Market
    market: Optional[str] = Field(None, alias="Market")
    source: Optional[str] = Field(None, alias="Source")
    neighborhood_rating: Optional[int] = Field(None, alias="Neighborhood_Rating")
    school_average: Optional[float] = Field(None, alias="School_Average")
    subdivision: Optional[str] = Field(None, alias="Subdivision")
    
    # Status
    reviewed_status: Optional[str] = Field(None, alias="Reviewed_Status")
    most_recent_status: Optional[str] = Field(None, alias="Most_Recent_Status")
    selling_reason: Optional[str] = Field(None, alias="Selling_Reason")
    final_reviewer: Optional[str] = Field(None, alias="Final_Reviewer")
    seller_retained_broker: Optional[str] = Field(None, alias="Seller_Retained_Broker")
    rent_restricted: Optional[str] = Field(None, alias="Rent_Restricted")
    
    # Nested records
    valuation: List[ValuationRecord] = Field(default_factory=list, alias="Valuation")
    hoa: List[HOARecord] = Field(default_factory=list, alias="HOA")
    rehab: List[RehabRecord] = Field(default_factory=list, alias="Rehab")
    
    @field_validator("sqft_total", mode="before")
    @classmethod
    def clean_sqft_total(cls, v):
        """Clean sqft from string like '5649 sqft' to float."""
        if v is None:
            return None
        if isinstance(v, str):
            numeric_str = "".join(c for c in v if c.isdigit() or c == ".")
            try:
                return float(numeric_str) if numeric_str else None
            except ValueError:
                return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None
    
    @field_validator("reviewed_status", "occupancy", "flood", mode="before")
    @classmethod
    def normalize_empty_strings(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v
    
    @field_validator("rent_restricted", "pool", "commercial", "htw", mode="before")
    @classmethod
    def normalize_yes_no_flags(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v_upper = v.strip().upper()
            if v_upper in ["YES", "NO"]:
                return v_upper
        return v
    
    model_config = {"populate_by_name": True}


class PropertyBatch(BaseModel):
    """Wrapper for batch processing multiple properties."""
    properties: List[Property]
    total_count: int = 0
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.total_count and self.properties:
            self.total_count = len(self.properties)
