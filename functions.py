def implode (list, pattern, delemiter):
    string = ""
    for index, value in list.iteritems():
        string = string + pattern.replace("{{index}}", index).replace("{{value}}", value) + delemiter

    return string.rstrip(delemiter)

def zeroPadding(str):
    integer = int(str)
    if integer < 10:
        return "0" + str(integer)
    else:
        return str(integer)