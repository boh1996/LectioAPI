def implode (list, pattern, delemiter):
    string = ""
    for index, value in list.iteritems():
        string = string + pattern.replace("{{index}}", index).replace("{{value}}", value) + delemiter

    return string.rstrip(delemiter)