def fix_date(date):
    date = date.split("/")
    if (len(date) == 3):
        date = [date[2], date[0], date[1]]
        return '"' + "-".join(date) + '"'
    else:
        return '"' + "".join(date) + '"'

def fix_second_date(date):
    date = date.split("/")
    if (len(date) == 3):
        time = date[2][4:]
        date = [date[2][:4], date[0], date[1]]
        return '"' + "-".join(date) + '"'
    else:
        return '"' + "".join(date) + '"'
