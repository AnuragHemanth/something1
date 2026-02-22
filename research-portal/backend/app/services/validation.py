def validate_numbers(data: dict):

    validated = {}

    for k, v in data.items():
        try:
            validated[k] = [float(x.replace(",", "")) for x in v]
        except:
            validated[k] = None

    return validated
