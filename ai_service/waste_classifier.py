"""
Waste Type Classification Module
Classifies detected waste into categories: Hazardous, Dry, Wet, Recyclable, E-Waste, Other
"""
from typing import Dict, List

# Waste type categories based on Indian waste management standards
WASTE_CATEGORIES = {
    'hazardous': {
        'keywords': ['battery', 'chemical', 'medical', 'syringe', 'toxic', 'paint', 'oil'],
        'coco_classes': [],  # COCO doesn't have explicit hazardous waste classes
        'priority': 'CRITICAL',
        'color': '#FF0000'
    },
    'wet': {
        'keywords': ['food', 'organic', 'vegetable', 'fruit', 'kitchen'],
        'coco_classes': [46, 47, 48, 49, 50, 51, 52, 53, 54, 55],  # Food items
        'priority': 'MEDIUM',
        'color': '#00AA00'
    },
    'dry': {
        'keywords': ['paper', 'cardboard', 'wrapper', 'packaging', 'box'],
        'coco_classes': [73, 84],  # Book, etc.
        'priority': 'LOW',
        'color': '#0066CC'
    },
    'recyclable': {
        'keywords': ['plastic', 'bottle', 'can', 'glass', 'metal'],
        'coco_classes': [39, 40, 41, 44, 45],  # Bottles, cups, bowls
        'priority': 'MEDIUM',
        'color': '#FFA500'
    },
    'e_waste': {
        'keywords': ['electronic', 'phone', 'computer', 'battery', 'wire', 'cable'],
        'coco_classes': [63, 64, 65, 66, 67, 73, 76],  # Electronics
        'priority': 'HIGH',
        'color': '#9900CC'
    }
}

def classify_waste_from_detections(detections: List[Dict], description: str = "") -> Dict:
    """
    Classify waste type based on YOLO detections and description keywords
    
    Args:
        detections: List of detected objects from YOLO
        description: User description text
    
    Returns:
        Dict containing:
        - primary_type: Main waste category
        - waste_composition: Percentage breakdown of waste types
        - is_hazardous: Boolean flag
        - is_mixed: Boolean if multiple types detected
        - recommendations: Disposal recommendations
    """
    
    # Count detections by waste type
    type_counts = {
        'hazardous': 0,
        'wet': 0,
        'dry': 0,
        'recyclable': 0,
        'e_waste': 0,
        'other': 0
    }
    
    total_objects = len(detections)
    
    if total_objects == 0:
        # No objects detected, check description for keywords
        description_lower = description.lower() if description else ""
        
        for waste_type, info in WASTE_CATEGORIES.items():
            for keyword in info['keywords']:
                if keyword in description_lower:
                    type_counts[waste_type] += 1
        
        # If still no classification, mark as other
        if sum(type_counts.values()) == 0:
            type_counts['other'] = 1
            total_objects = 1
    else:
        # Classify based on detected objects
        for detection in detections:
            class_id = detection.get('class_id')
            class_name = detection.get('class_name', '').lower()
            
            classified = False
            
            # Check COCO class IDs
            for waste_type, info in WASTE_CATEGORIES.items():
                if class_id in info['coco_classes']:
                    type_counts[waste_type] += 1
                    classified = True
                    break
            
            # Check class name keywords
            if not classified:
                for waste_type, info in WASTE_CATEGORIES.items():
                    for keyword in info['keywords']:
                        if keyword in class_name:
                            type_counts[waste_type] += 1
                            classified = True
                            break
                    if classified:
                        break
            
            # If still not classified, mark as other
            if not classified:
                type_counts['other'] += 1
        
        # Also check description for additional context
        if description:
            description_lower = description.lower()
            for waste_type, info in WASTE_CATEGORIES.items():
                for keyword in info['keywords']:
                    if keyword in description_lower:
                        # Give bonus weight to description matches
                        type_counts[waste_type] += 0.5
    
    # Calculate percentages
    total = sum(type_counts.values())
    waste_composition = {}
    
    for waste_type, count in type_counts.items():
        if count > 0:
            percentage = round((count / total) * 100, 1)
            waste_composition[waste_type] = percentage
    
    # Determine primary type (highest percentage)
    if waste_composition:
        primary_type = max(waste_composition.items(), key=lambda x: x[1])[0]
    else:
        primary_type = 'other'
    
    # Check if hazardous
    is_hazardous = type_counts['hazardous'] > 0 or (
        description and any(kw in description.lower() for kw in WASTE_CATEGORIES['hazardous']['keywords'])
    )
    
    # Check if mixed waste
    significant_types = [t for t, p in waste_composition.items() if p >= 20]
    is_mixed = len(significant_types) > 1
    
    # Generate recommendations
    recommendations = _generate_disposal_recommendations(
        primary_type, 
        is_hazardous, 
        is_mixed,
        waste_composition
    )
    
    return {
        'primary_type': primary_type,
        'waste_composition': waste_composition,
        'is_hazardous': is_hazardous,
        'is_mixed': is_mixed,
        'recommendations': recommendations,
        'priority_level': WASTE_CATEGORIES.get(primary_type, {}).get('priority', 'MEDIUM')
    }

def _generate_disposal_recommendations(
    primary_type: str,
    is_hazardous: bool,
    is_mixed: bool,
    composition: Dict
) -> List[str]:
    """Generate disposal and handling recommendations"""
    
    recommendations = []
    
    if is_hazardous:
        recommendations.append("⚠️ HAZARDOUS WASTE - Requires specialized disposal")
        recommendations.append("Contact hazardous waste management authority")
        recommendations.append("Do not mix with regular waste")
    
    if is_mixed:
        recommendations.append("Mixed waste detected - Segregation required")
        recommendations.append("Separate into dry, wet, and recyclable categories")
    
    # Type-specific recommendations
    if primary_type == 'wet':
        recommendations.append("Wet waste: Suitable for composting")
        recommendations.append("Collect in green bins")
    elif primary_type == 'dry':
        recommendations.append("Dry waste: Can be sent to recycling")
        recommendations.append("Collect in blue bins")
    elif primary_type == 'recyclable':
        recommendations.append("Recyclable materials detected")
        recommendations.append("Clean and send to recycling facility")
        if composition.get('recyclable', 0) > 50:
            recommendations.append("High recyclable content - Good for resource recovery")
    elif primary_type == 'e_waste':
        recommendations.append("E-waste detected - Special handling required")
        recommendations.append("Contact authorized e-waste recycler")
        recommendations.append("Do not dispose in regular bins")
    
    if not recommendations:
        recommendations.append("Regular waste disposal procedures apply")
    
    return recommendations

def get_waste_type_summary(waste_classification: Dict) -> str:
    """Generate human-readable summary of waste type"""
    
    primary = waste_classification['primary_type'].replace('_', '-').title()
    composition = waste_classification['waste_composition']
    
    if waste_classification['is_hazardous']:
        return f"⚠️ Hazardous {primary} Waste"
    elif waste_classification['is_mixed']:
        types = [t.replace('_', '-').title() for t, p in composition.items() if p >= 15]
        return f"Mixed Waste ({', '.join(types[:3])})"
    else:
        return f"{primary} Waste"
