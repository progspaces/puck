def clamp(value, lowerbound, upperbound):
    if value < lowerbound:
        return lowerbound
    elif value > upperbound:
        return upperbound
    return value