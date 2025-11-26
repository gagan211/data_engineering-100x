"""Transform module: Convert Property objects into normalized database rows."""

import logging
from typing import List, Dict, Tuple, Any
from src.models import Property

logger = logging.getLogger(__name__)


def transform_properties_to_facts(properties: List[Property]) -> Dict[str, List[Dict[str, Any]]]:
    """Transform denormalized Property objects into normalized table rows."""
    facts = {
        "properties": [],
        "valuations": [],
        "hoa_fees": [],
        "rehab_assessments": []
    }
    
    logger.info(f"Transforming {len(properties)} properties to facts")
    
    for property_obj in properties:
        property_row = {
            "property_title": property_obj.property_title,
            "address": property_obj.address,
            "street_address": property_obj.street_address,
            "city": property_obj.city,
            "state": property_obj.state,
            "zip_code": property_obj.zip_code,
            "latitude": property_obj.latitude,
            "longitude": property_obj.longitude,
            "property_type": property_obj.property_type,
            "year_built": property_obj.year_built,
            "sqft_total": property_obj.sqft_total,
            "sqft_basement": property_obj.sqft_basement,
            "sqft_mu": property_obj.sqft_mu,
            "bed": property_obj.bed,
            "bath": property_obj.bath,
            "layout": property_obj.layout,
            "pool": property_obj.pool,
            "parking": property_obj.parking,
            "basement_yes_no": property_obj.basement_yes_no,
            "water": property_obj.water,
            "sewage": property_obj.sewage,
            "htw": property_obj.htw,
            "commercial": property_obj.commercial,
            "highway": property_obj.highway,
            "train": property_obj.train,
            "flood": property_obj.flood,
            "occupancy": property_obj.occupancy,
            "net_yield": property_obj.net_yield,
            "irr": property_obj.irr,
            "taxes": property_obj.taxes,
            "tax_rate": property_obj.tax_rate,
            "market": property_obj.market,
            "source": property_obj.source,
            "neighborhood_rating": property_obj.neighborhood_rating,
            "school_average": property_obj.school_average,
            "subdivision": property_obj.subdivision,
            "reviewed_status": property_obj.reviewed_status,
            "most_recent_status": property_obj.most_recent_status,
            "selling_reason": property_obj.selling_reason,
            "final_reviewer": property_obj.final_reviewer,
            "seller_retained_broker": property_obj.seller_retained_broker,
            "rent_restricted": property_obj.rent_restricted,
        }
        facts["properties"].append(property_row)
        
        property_id = len(facts["properties"])
        
        for val_idx, val_record in enumerate(property_obj.valuation):
            valuation_row = {
                "property_id": property_id,
                "valuation_index": val_idx + 1,
                "list_price": val_record.list_price,
                "previous_rent": val_record.previous_rent,
                "arv": val_record.arv,
                "rent_zestimate": val_record.rent_zestimate,
                "low_fmr": val_record.low_fmr,
                "high_fmr": val_record.high_fmr,
                "zestimate": val_record.zestimate,
                "expected_rent": val_record.expected_rent,
                "redfin_value": val_record.redfin_value,
            }
            facts["valuations"].append(valuation_row)
        
        for hoa_idx, hoa_record in enumerate(property_obj.hoa):
            hoa_row = {
                "property_id": property_id,
                "hoa_index": hoa_idx + 1,
                "hoa_amount": hoa_record.hoa_amount,
                "hoa_flag": hoa_record.hoa_flag,
            }
            facts["hoa_fees"].append(hoa_row)
        
        for rehab_idx, rehab_record in enumerate(property_obj.rehab):
            rehab_row = {
                "property_id": property_id,
                "rehab_index": rehab_idx + 1,
                "underwriting_rehab": rehab_record.underwriting_rehab,
                "rehab_calculation": rehab_record.rehab_calculation,
                "paint": rehab_record.paint,
                "flooring_flag": rehab_record.flooring_flag,
                "foundation_flag": rehab_record.foundation_flag,
                "roof_flag": rehab_record.roof_flag,
                "hvac_flag": rehab_record.hvac_flag,
                "kitchen_flag": rehab_record.kitchen_flag,
                "bathroom_flag": rehab_record.bathroom_flag,
                "appliances_flag": rehab_record.appliances_flag,
                "windows_flag": rehab_record.windows_flag,
                "landscaping_flag": rehab_record.landscaping_flag,
                "trashout_flag": rehab_record.trashout_flag,
            }
            facts["rehab_assessments"].append(rehab_row)
    
    logger.info(
        f"Transformation complete: "
        f"{len(facts['properties'])} properties, "
        f"{len(facts['valuations'])} valuations, "
        f"{len(facts['hoa_fees'])} HOA records, "
        f"{len(facts['rehab_assessments'])} rehab records"
    )
    
    return facts


def extract_dimension_values(facts: Dict[str, List[Dict[str, Any]]]) -> Dict[str, set]:
    """Extract unique dimension values from facts."""
    dimensions = {
        "markets": set(),
        "sources": set(),
        "property_types": set(),
        "layouts": set(),
    }
    
    for prop in facts["properties"]:
        if prop.get("market"):
            dimensions["markets"].add(prop["market"])
        if prop.get("source"):
            dimensions["sources"].add(prop["source"])
        if prop.get("property_type"):
            dimensions["property_types"].add(prop["property_type"])
        if prop.get("layout"):
            dimensions["layouts"].add(prop["layout"])
    
    logger.info(
        f"Extracted dimensions: "
        f"{len(dimensions['markets'])} markets, "
        f"{len(dimensions['sources'])} sources, "
        f"{len(dimensions['property_types'])} types, "
        f"{len(dimensions['layouts'])} layouts"
    )
    
    return dimensions


def transform_properties(properties: List[Property]) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, set]]:
    """Main transformation orchestration."""
    facts = transform_properties_to_facts(properties)
    dimensions = extract_dimension_values(facts)
    return facts, dimensions
