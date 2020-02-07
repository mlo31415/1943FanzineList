#-----------------------------
# Helper function
# Try to make the input numeric
# Note that if it fails, it returns what came in.
def ToNumeric(val):
    if val == None:
        return None

    if isinstance(val, str) and len(val.strip()) == 0:  # Empty strings become None
        return None

    if isinstance(val, int) or isinstance(val, float):  # Numbers are numbers and just get returned
        return val

    # Last chance is to try to convert the vale into an int or float.
    try:
        return int(val)
    except:
        try:
            return float(val)
        except:
            return val  #Foiled on all fronts; Just return the input value -- whatever it is.


#==================================================================================
# Return a properly formatted link
def FormatLink(url: str, text: str):
    # TODO: Do we need to deal with turning blanks into %20 whatsits?
    # If the url points to a pdf, add '#view=Fit' to the end to force the PDF to scale to the page
    if url.lower().endswith(".pdf"):
        url+="#view=Fit"
    return '<a href='+url+'>'+text+'</a>'