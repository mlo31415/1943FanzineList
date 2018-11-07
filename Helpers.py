def TC(s):
    ls=s.lower()
    if ls == "a" or ls == "an" or ls == "the":
        return ls

def TitleCase(str):
    str=" ".join([TC(s) for s in str.split(" ")])
