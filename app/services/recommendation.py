from typing import List, Dict


def generate_recommendations(
    disease: str,
    severity: str,
    risk_level: str,
    crop: str
) -> List[Dict]:

    recommendations = []

    # --------------------------------
    # General monitoring
    # --------------------------------

    recommendations.append({
        "priority": "high",
        "type": "monitoring",
        "action": "Inspect affected plants and nearby plants regularly.",
        "reason": "Early detection can help prevent further spread."
    })

    # --------------------------------
    # Low risk
    # --------------------------------

    if risk_level == "low":

        recommendations.append({
            "priority": "medium",
            "type": "cultural",
            "action": "Remove severely affected leaves or plant parts.",
            "reason": "Reduces potential disease or pest spread."
        })

        recommendations.append({
            "priority": "medium",
            "type": "monitoring",
            "action": "Recheck the crop within 3 to 5 days.",
            "reason": "Monitor whether symptoms are increasing."
        })

    # --------------------------------
    # Medium risk
    # --------------------------------

    elif risk_level == "medium":

        recommendations.append({
            "priority": "high",
            "type": "cultural",
            "action": "Remove and safely dispose of heavily affected plant parts.",
            "reason": "Can reduce the source of infection."
        })

        recommendations.append({
            "priority": "high",
            "type": "field_management",
            "action": "Avoid unnecessary overhead irrigation and improve field ventilation.",
            "reason": "Excess moisture can favor several crop diseases."
        })

        recommendations.append({
            "priority": "medium",
            "type": "monitoring",
            "action": "Monitor the field closely over the next 2 to 3 days.",
            "reason": "Medium-risk conditions may develop into a more serious outbreak."
        })

    # --------------------------------
    # High risk
    # --------------------------------

    elif risk_level == "high":

        recommendations.append({
            "priority": "high",
            "type": "immediate_action",
            "action": "Inspect the entire field and identify additional affected areas.",
            "reason": "High-risk conditions require rapid assessment."
        })

        recommendations.append({
            "priority": "high",
            "type": "cultural",
            "action": "Remove and safely dispose of severely affected plant material where appropriate.",
            "reason": "Helps reduce disease or pest pressure."
        })

        recommendations.append({
            "priority": "high",
            "type": "expert",
            "action": "Consider contacting an agricultural expert or local extension service for confirmation.",
            "reason": "High-risk cases should be verified before major treatment decisions."
        })

    # --------------------------------
    # Safety recommendation
    # --------------------------------

    recommendations.append({
        "priority": "high",
        "type": "safety",
        "action": "Do not apply pesticides solely from an AI diagnosis. Verify the problem and follow the product label and local agricultural guidance.",
        "reason": "Incorrect pesticide use can harm crops, people, beneficial organisms, and the environment."
    })

    return recommendations
