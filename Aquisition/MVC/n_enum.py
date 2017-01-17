def enum(*enumerated):
    enums = dict(zip(enumerated,range(len(enumerated))))
    enums["names"] = enumerated
    return type('enum',(),enums)
