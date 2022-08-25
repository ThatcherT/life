import datetime

def get_date_from_weekday(weekday):
    """
    Returns a date object from a given weekday.
    :param weekday: int
    :return: date
    """
    
    now = datetime.datetime.today()
    current_weekday = now.weekday()

    if current_weekday == weekday:
        return now
    elif current_weekday < weekday:
        return now + datetime.timedelta(days=weekday - current_weekday)
    elif current_weekday > weekday:
        return now + datetime.timedelta(days=7) - datetime.timedelta(days=current_weekday - weekday)
    