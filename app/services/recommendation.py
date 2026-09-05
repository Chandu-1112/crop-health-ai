from typing import List, Dict


def generate_recommendations(
    disease: str,
    severity: str,
    risk_level: str,
    crop: str,
    language: str = "en",
) -> List[Dict]:
    labels = {
        "en": {
            "inspect": "Inspect affected plants and nearby plants regularly.",
            "early": "Early detection can help prevent further spread.",
            "hygiene": "Remove infected plant debris, disinfect tools, avoid working in wet foliage, and monitor nearby plants.",
            "hygiene_reason": "Good field hygiene reduces spread while the diagnosis is confirmed.",
            "remove": "Remove severely affected leaves or plant parts.",
            "remove_reason": "Reduces potential disease or pest spread.",
            "recheck": "Recheck the crop within 3 to 5 days.",
            "recheck_reason": "Monitor whether symptoms are increasing.",
            "dispose": "Remove and safely dispose of heavily affected plant parts.",
            "dispose_reason": "Can reduce the source of infection.",
            "irrigation": "Avoid unnecessary overhead irrigation and improve field ventilation.",
            "irrigation_reason": "Excess moisture can favor several crop diseases.",
            "close": "Monitor the field closely over the next 2 to 3 days.",
            "close_reason": "Medium-risk conditions may develop into a more serious outbreak.",
            "entire": "Inspect the entire field and identify additional affected areas.",
            "entire_reason": "High-risk conditions require rapid assessment.",
            "severe": "Remove and safely dispose of severely affected plant material where appropriate.",
            "severe_reason": "Helps reduce disease or pest pressure.",
            "expert": "Contact an agricultural expert or local extension service for confirmation.",
            "expert_reason": "High-risk cases should be verified before major treatment decisions.",
            "safety": "Do not spray pesticides solely from an AI diagnosis. Confirm the pest or disease, use only a locally registered product for this crop, and follow the label dose, protective equipment, pre-harvest interval, and extension advice.",
            "safety_reason": "Incorrect pesticide use can harm crops, people, beneficial organisms, and the environment.",
        },
        "te": {
            "inspect": "బాధిత మొక్కలను మరియు పక్క మొక్కలను క్రమం తప్పకుండా పరిశీలించండి.",
            "early": "ముందస్తు గుర్తింపు వ్యాధి లేదా పురుగు వ్యాప్తిని తగ్గిస్తుంది.",
            "hygiene": "బాధిత మొక్క అవశేషాలను తొలగించి, పనిముట్లను శుభ్రపరచి, తడి ఆకులపై పని చేయకుండా, పక్క మొక్కలను గమనించండి.",
            "hygiene_reason": "నిర్ధారణ అయ్యే వరకు పొలం పరిశుభ్రత వ్యాప్తిని తగ్గిస్తుంది.",
            "remove": "తీవ్రంగా బాధిత ఆకులు లేదా మొక్క భాగాలను తొలగించండి.",
            "remove_reason": "వ్యాధి లేదా పురుగు వ్యాప్తి అవకాశాన్ని తగ్గిస్తుంది.",
            "recheck": "3 నుండి 5 రోజుల్లో పంటను మళ్లీ పరిశీలించండి.",
            "recheck_reason": "లక్షణాలు పెరుగుతున్నాయా గమనించండి.",
            "dispose": "బాధిత మొక్క భాగాలను తొలగించి సురక్షితంగా పారవేయండి.",
            "dispose_reason": "సంక్రమణ మూలాన్ని తగ్గించవచ్చు.",
            "irrigation": "అవసరం లేని పైపొర నీటిపారుదల నివారించి, పొలంలో గాలి ప్రసరణ పెంచండి.",
            "irrigation_reason": "అధిక తేమ కొన్ని పంట వ్యాధులకు అనుకూలంగా ఉంటుంది.",
            "close": "తదుపరి 2 నుండి 3 రోజులు పొలాన్ని జాగ్రత్తగా గమనించండి.",
            "close_reason": "మధ్యస్థ ప్రమాదం తీవ్రమైన వ్యాప్తిగా మారవచ్చు.",
            "entire": "మొత్తం పొలాన్ని పరిశీలించి అదనపు బాధిత ప్రాంతాలను గుర్తించండి.",
            "entire_reason": "అధిక ప్రమాద పరిస్థితులకు వేగవంతమైన పరిశీలన అవసరం.",
            "severe": "అవసరమైన చోట తీవ్రంగా బాధిత మొక్క పదార్థాన్ని తొలగించి సురక్షితంగా పారవేయండి.",
            "severe_reason": "వ్యాధి లేదా పురుగు ఒత్తిడిని తగ్గించడంలో సహాయపడుతుంది.",
            "expert": "నిర్ధారణ కోసం వ్యవసాయ నిపుణుడిని లేదా స్థానిక విస్తరణ అధికారిని సంప్రదించండి.",
            "expert_reason": "పెద్ద చికిత్స నిర్ణయాల ముందు అధిక ప్రమాద కేసులను నిర్ధారించాలి.",
            "safety": "AI నిర్ధారణ ఆధారంగా మాత్రమే పురుగుమందు పిచికారీ చేయవద్దు. పురుగు లేదా వ్యాధిని నిర్ధారించి, ఈ పంటకు స్థానికంగా నమోదైన ఉత్పత్తిని మాత్రమే లేబుల్ మోతాదు, రక్షణ పరికరాలు, కోతకు ముందు విరామం మరియు వ్యవసాయ సలహా ప్రకారం వాడండి.",
            "safety_reason": "తప్పు పురుగుమందు వాడకం పంటలు, మనుషులు, ప్రయోజనకర జీవులు మరియు పర్యావరణానికి హాని చేస్తుంది.",
        },
        "hi": {
            "inspect": "प्रभावित और आसपास के पौधों की नियमित जांच करें.",
            "early": "जल्दी पहचान से रोग या कीट का फैलाव कम हो सकता है.",
            "hygiene": "संक्रमित अवशेष हटाएं, औजार साफ करें, गीली पत्तियों पर काम न करें और आसपास के पौधों पर नजर रखें.",
            "hygiene_reason": "जांच पूरी होने तक खेत की स्वच्छता फैलाव कम करती है.",
            "remove": "बहुत प्रभावित पत्तियां या पौधे के हिस्से हटाएं.",
            "remove_reason": "रोग या कीट के फैलाव की संभावना कम होती है.",
            "recheck": "3 से 5 दिनों में फसल की फिर जांच करें.",
            "recheck_reason": "देखें कि लक्षण बढ़ रहे हैं या नहीं.",
            "dispose": "अधिक प्रभावित हिस्सों को हटाकर सुरक्षित तरीके से नष्ट करें.",
            "dispose_reason": "संक्रमण के स्रोत को कम किया जा सकता है.",
            "irrigation": "अनावश्यक ऊपर से सिंचाई न करें और खेत में हवा का प्रवाह बढ़ाएं.",
            "irrigation_reason": "अधिक नमी कई फसल रोगों को बढ़ावा दे सकती है.",
            "close": "अगले 2 से 3 दिनों तक खेत की करीब से निगरानी करें.",
            "close_reason": "मध्यम जोखिम गंभीर प्रकोप में बदल सकता है.",
            "entire": "पूरे खेत की जांच कर अतिरिक्त प्रभावित क्षेत्रों की पहचान करें.",
            "entire_reason": "उच्च जोखिम में तुरंत जांच जरूरी है.",
            "severe": "जहां उचित हो, गंभीर रूप से प्रभावित पौधों को हटाकर सुरक्षित तरीके से नष्ट करें.",
            "severe_reason": "रोग या कीट का दबाव कम करने में मदद मिलती है.",
            "expert": "पुष्टि के लिए कृषि विशेषज्ञ या स्थानीय विस्तार अधिकारी से संपर्क करें.",
            "expert_reason": "बड़े उपचार निर्णयों से पहले उच्च जोखिम मामलों की पुष्टि जरूरी है.",
            "safety": "केवल AI जांच के आधार पर कीटनाशक का छिड़काव न करें. कीट या रोग की पुष्टि करें, इस फसल के लिए स्थानीय रूप से पंजीकृत उत्पाद ही लें और लेबल मात्रा, सुरक्षा उपकरण, कटाई-पूर्व अंतराल और कृषि सलाह का पालन करें.",
            "safety_reason": "गलत कीटनाशक उपयोग से फसल, लोग, लाभकारी जीव और पर्यावरण को नुकसान हो सकता है.",
        },
    }.get(language, {})

    recommendations = []

    # --------------------------------
    # General monitoring
    # --------------------------------

    recommendations.append({
        "priority": "high",
        "type": "monitoring",
        "action": labels["inspect"],
        "reason": labels["early"]
    })

    recommendations.append({
        "priority": "high",
        "type": "prevention",
        "action": labels["hygiene"],
        "reason": labels["hygiene_reason"]
    })

    # --------------------------------
    # Low risk
    # --------------------------------

    if risk_level == "low":

        recommendations.append({
            "priority": "medium",
            "type": "cultural",
            "action": labels["remove"],
            "reason": labels["remove_reason"]
        })

        recommendations.append({
            "priority": "medium",
            "type": "monitoring",
            "action": labels["recheck"],
            "reason": labels["recheck_reason"]
        })

    # --------------------------------
    # Medium risk
    # --------------------------------

    elif risk_level == "medium":

        recommendations.append({
            "priority": "high",
            "type": "cultural",
            "action": labels["dispose"],
            "reason": labels["dispose_reason"]
        })

        recommendations.append({
            "priority": "high",
            "type": "field_management",
            "action": labels["irrigation"],
            "reason": labels["irrigation_reason"]
        })

        recommendations.append({
            "priority": "medium",
            "type": "monitoring",
            "action": labels["close"],
            "reason": labels["close_reason"]
        })

    # --------------------------------
    # High risk
    # --------------------------------

    elif risk_level == "high":

        recommendations.append({
            "priority": "high",
            "type": "immediate_action",
            "action": labels["entire"],
            "reason": labels["entire_reason"]
        })

        recommendations.append({
            "priority": "high",
            "type": "cultural",
            "action": labels["severe"],
            "reason": labels["severe_reason"]
        })

        recommendations.append({
            "priority": "high",
            "type": "expert",
            "action": labels["expert"],
            "reason": labels["expert_reason"]
        })

    # --------------------------------
    # Safety recommendation
    # --------------------------------

    recommendations.append({
        "priority": "high",
        "type": "pesticide_safety",
        "action": labels["safety"],
        "reason": labels["safety_reason"]
    })

    return recommendations
