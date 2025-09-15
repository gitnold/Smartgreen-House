
#calculate moving average using latest five soil Soil Moisture statistics

def wateringControl(inputs: dict ) -> str:
    #watering level
    for key in inputs:
        inputs[key] = int(inputs[key])
    
    #FIX: btn 50 and 70 edge case
    if (inputs['Soil Moisture'] < 35) and (inputs['Humidity'] < 40 or inputs['Temperature'] > 30):
        return (f"{inputs['Soil Moisture']}: Watering plants...")

    elif (35 < inputs['Soil Moisture'] < 50) and (inputs['Temperature'] > 35):
        return (f"{inputs['Soil Moisture']}: Initiating Light watering")

    elif inputs['Soil Moisture'] > 70:
         return (f"{inputs['Soil Moisture']}: No watering")
    #TODO: use trends to infer missing ranges.
    else:
        return "No action"



def shadingControl(inputs: dict) -> str:
    #make sure input is a number in the first place.
    #choose on what to return for the dashboard claculations.
    match inputs['Light']:
        case lux if lux < 300:
            return "Opening shades"
        case lux if 300 <= lux < 800:
            return "No action"
        case lux if 800 <= lux <= 1000:
            return "Close partially"
        case lux if lux > 1000:
            return "Close fully"
        case _:
            return "Unknown input format"

    
def raiseAlert(inputs: dict) -> bool:
    # Write more concise logic for checks below.
    # Condition #: more than two alerts are consecutive.
    alert_count = 0
    
    if inputs['Temperature'] > 36:
        alert_count += 1
    if inputs['Humidity'] < 25:
        alert_count += 1
    if inputs['Carbon IV Oxide'] > 1200:
        alert_count += 1
    if inputs['Soil Moisture'] < 30:
        alert_count += 1
    if inputs['Light'] > 1100:
        alert_count += 1
    
    return alert_count >= 3
