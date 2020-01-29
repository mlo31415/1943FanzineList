#-----------------------------
# Helper function
# Try to make the input numeric
# Note that if it fails, it returns what came in.
def ToNumeric(val):
    if val == None:
        return None

    if isinstance(val, int) or isinstance(val, float):
        return val

    try:
        return int(val)
    except:
        try:
            return float(val)
        except:
            return val