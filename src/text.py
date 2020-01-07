import re

# (\W|\A)(A){2,3}|(B){2,3}|(C){2,3})(\+|-)?(\W|\A)
MoodyPattern = re.compile(r"(\W|\A)[ABC](a[1-3]|a{2}|a{2}[1-3]|[1-3])(\W|\A)")
FandS_PPattern = re.compile(r"(\W|\A)(((A){2,3}|(B){2,3}|(C){2,3})(\+|-)?)|((A(\+|-))|(B(\+|-))|(C(\+|-)))(\W|\A)")

valid_charsMoody = ['a', 'A', 'B', 'C', '1', '2', '3']
valid_charsFitch = ['A', 'B', 'C', '+', '-']

def onlyValidMoody(string):
    if string is None:
        return None
    i = 0
    while i != len(string):
        if (not string[i] in valid_charsMoody):
            string = string[:i] + string[i + 1:]
        else:
            i += 1
    return string

def onlyValidFitch(string):
    if string is None:
        return None
    i = 0
    while i != len(string):
        if (not string[i] in valid_charsFitch):
            string = string[:i] + string[i + 1:]
        else:
            i += 1
    return string

def getFitch(text):
    if text == "NULL":
        return "NULL"
    fitch_ratings = []
    fitch = FandS_PPattern.match(text)
    if not fitch is None:
        i = 0
        try:
            val = onlyValidFitch(fitch.group(i))
        except IndexError:
            return "NULL"
        while not val is None:
            if not val in fitch_ratings and len(val) > 1:
                fitch_ratings.append(val)
            i += 1
            try:
                val = onlyValidFitch(fitch.group(i))
            except IndexError:
                break
    if len(fitch_ratings) > 0:
        return '|'.join(fitch_ratings)
    else:
        return "NULL"

def getMoody(text):
    if text == "NULL":
        return "NULL"
    moody_ratings = []
    mood = MoodyPattern.match(text)
    if not mood is None:
        i = 0
        try:
            val = onlyValidMoody(mood.group(i))
        except IndexError:
            return "NULL"
        while not val is None:
            if not val in moody_ratings and len(val) > 1:
                moody_ratings.append(val)
            i += 1
            try:
                val = onlyValidMoody(mood.group(i))
            except IndexError:
                break
    if len(moody_ratings) > 0:
        return '|'.join(moody_ratings)
    else:
        return "NULL"




