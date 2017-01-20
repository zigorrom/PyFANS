##def enum(*enumerated):
##    enums = dict(zip(enumerated,range(len(enumerated))))
##    enums["names"] = enumerated
##    return type('enum',(),enums)


##a = enum("asdad","a1")
##print (a.a1)




def enum( *enumerated,name_prefix = ""):

    g = [name_prefix+e for e in enumerated]
    enums = dict(zip(g,range(len(enumerated))))
    enums["names"] = tuple(g)
    enums["values"] = enumerated
##    print(enums)
    return type('enum',(),enums)


##AI_CHANNELS = enum("AI_1","AI_2","AI_3","AI_4",name_prefix = "a_")
##print(AI_CHANNELS.values[AI_CHANNELS.a_AI_1])
