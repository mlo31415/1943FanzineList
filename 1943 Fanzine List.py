import re as Regex
from IssueSpec import IssueSpec, IssueSpecList
from FanzineSeriesSpec import FanzineSeriesSpec
from FanacIssueData import FanacIssueData

def DecodeIssueList(issuesText):
    if issuesText is None:    # Skip empty stuff
        return None
    if len(issuesText.strip()) == 0: # Skip if it's all whitespace
        return None

    # Turn all multiple spaces into a single space
    issuesText=issuesText.replace("  ", " ").replace("  ", " ").replace("  ", " ").strip()   # Hopefully there's never more than 8 spaces in succession...

    isl=IssueSpecList()   # This will be the list of IssueSpecs resulting from interpreting stuff

    # Cases:
    #   1,2,3,4
    #   V1#2, V3#4
    #   V1#2,3 or V1:2,3
    #   1942:5
    #   210-223
    #   Sometimes a semicolon is used as a separator....
    #   The different representations can be intermixed.  This causes a problem because the comma winds up having different meanings in different cases.
    #   Stuff in parentheses will always be treated as comments
    #   Trailing '?' will be ignored
    #   And sometimes there is odd stuff tossed in which can't be interpreted.

    # The strategy is to take the string character by character and whittle stuff down as we interpret it.
    # The intention is that we come back to the start of the look each time we have disposed of a chunk of characters, so that the next character should start a new issue designation
    # The intention is that we come back to the start of the look each time we have disposed of a chunk of characters, so that the next character should start a new issue designation
    # There are four basic patterns to be seen in Joe's data:
    #   A comma-separated list of issue whole numners
    #   A list of Volumes and numbers (many delimiter patterns!)
    #   A range of whole numbers
    #   A list of year:issue pairs
    #  In all cases we need to be prepared to deal with (and preserve) random text.

    # Walk the issue spec decoding it as we go.
    while len(issuesText) > 0:
        issuesText=issuesText.strip()  # Leading and trailing whitespace is uninteresting
        if issuesText[0] == ",":
            issuesText=issuesText[1:].strip()   # If the previous pass just took a piece of a comma-separated list, remove the leading comma and any associated wihtespace
        # And try again
        issuesText=InterpretIssueSpec(isl, issuesText)

    print("   "+isl.Format())
    print("   "+isl.Str())
    return isl

# Interpret some or all of the input text (from islText) as an issue spec list and append the interpreted ISs we find to isl
# It's permissible to not handle the complete list in oen go, since we are called repeatedly until islText is completely interpreted.
def InterpretIssueSpec(isl, islText):
    islText=islText.strip()

    # OK, now try to decode the spec, update the isl, and return whatever text can't be handled this round
    # We'll try several alteratives

    # First:
    #   Vnn#nn
    #   Vnn:nn
    #   Vnn#nn,nn,nn
    #   Vnn:nn,nn,nn
    c_VnnNnn=Regex.compile(r"""^    # Start at the beginning
                [vV](\d+\s*)        # Look for a V followed by 1 or more digits
                [#:]\s*             # Then a '#' or a ':' followed by option whitespace
                ((?:\d+,\s*)*)      # Then a non-capturing group of one or more digits followed by a comma followed by optional whitespace
                                    # this whole thing is a group that matches many of the non-capturing groups 
                (\d+[;,]?)(.*)      # Then a last group of digits which must be present followed by an optional comma followed by the rest of the line
                """, Regex.X)
    m=c_VnnNnn.match(islText)
    if m != None and len(m.groups()) == 4:
        vol=int(m.groups()[0])
        # Create iList, which is a list of issues associated with this volume number
        iList=m.groups()[1]+m.groups()[2]
        islText=m.groups()[3]
        iList=iList.replace(" ", "").replace(";", ",").split(",")  # Split on either ',' or ':'
        for i in iList:
            if len(i) == 0:
                continue
            t=IssueSpec(Vol=vol, Num=i)
            isl.AppendIS(t)

        # Check to see if the last item was followed by a bracketed comment.  If so, add it to the last item.
        if len(iList) > 0:
            islText=islText.strip()
            if len(islText) > 0:
                t=isl.List()[-1:]   # Get the last element of the list
                if islText[0] == '[':
                    m=Regex.compile("^(\[.*\])(.*)$").match(islText)
                    if m is not None and len(m.groups()) == 2:
                        t=IssueSpec()
                        t.TrailingGarbage=m.groups()[0]
                        islText=m.groups()[1].strip()
                        if len(islText) > 0 and islText[0] == ",":
                            islText=islText[1:].strip()  # If there was a trailing comma, delete it.
                elif islText[0] == '(':
                    m=Regex.match("^(\(.*\))(.*)$", islText)
                    if m is not None and len(m.groups()) == 2:
                        t=IssueSpec()
                        t.TrailingGarbage=m.groups()[0]
                        islText=m.groups()[1].strip()
                        if len(islText) > 0 and islText[0] == ",":
                            islText=islText[1:].strip()  # If there was a trailing comma, delete it.
                isl[-1:]=t

        return islText   # Return the unmatched part of the string

    # Second, deal with a range of numbers, nnn-nnn
    # Look at two cases, (1) a range all by itself and (2) A range in a list (i.e., followed by a comma)
    m=Regex.match("^(\d+)\s*[\-–]\s*(\d+)$", islText)   # First, a range all by itself
    if m is not None and len(m.groups()) == 2:
        for k in range(int(m.groups()[0]), int(m.groups()[1])+1):
            isl.AppendIS(IssueSpec(Whole=k))
        return ""    # By definition the line is now empty
    m=Regex.match("^(\d+)\s*[\-–]\s*(\d+),", islText)   # Now a range which is part of a list (Note that we terminate on a comma rather than EOL
    if m is not None and len(m.groups()) == 2:
        for k in range(int(m.groups()[0]), int(m.groups()[1])+1):
            isl.AppendIS(IssueSpec(Whole=k))
        return m.string[m.lastindex+1:]   # Return the unmatched part of the string


    # Next, consider a list of years or year-month pairs:
    # yyyy[, yyyy]
    # yyyy:mm[, yyyy:mm]
    # The years *must* be 4-digit so we can tell them apart from just-plain-numbers
    # There are two cases, alone on the line and as part of a comma-separated list
    # Year alone
    m=Regex.match("^(\d{4})$", islText)
    if m is not None and len(m.groups()) > 0:
        isl.AppendIS(IssueSpec().SetDate(m.groups()[0], None))
        return ""   # By definition the line is now empty

    # Year comma-terminated
    m=Regex.match("^(\d{4})\s*,", islText)
    if m is not None and len(m.groups()) > 0:
        isl.AppendIS(IssueSpec().SetDate(m.groups()[0], None))
        return m.string[m.lastindex:]   # Return the unmatched part of the string

    # Year:month alone
    m=Regex.match("^(\d{4}):(\d+)$", islText)
    if m is not None and len(m.groups()) > 0:
        isl.AppendIS(IssueSpec().SetDate(m.groups()[0], m.groups()[1]))
        return ""  # By definition the line is now empty

    # Year:month comma-terminated
    m=Regex.match("^(\d{4}):(\d+)\s*,", islText)
    if m is not None and len(m.groups()) > 0:
        isl.AppendIS(IssueSpec().SetDate(m.groups()[0], m.groups()[1]))
        return m.string[m.lastindex:]  # Return the unmatched part of the string


    # Now consider it as a simple list of whole numbers (perhaps with a trailing alphabetic character, e.g, 24, 25, 25A, 26) (and perhaps with a # in front of the number, e.g., #2)
    # So we want to match <optional whitespace><digits><optional alphas><optional whitespace><comma>
    m=Regex.match("^#?([0-9]+)([a-zA-Z]*)\s*,", islText)
    if m is not None and len(m.groups()) > 0:
        t=IssueSpec(Whole=m.groups()[0])
        t.TrailingGarbage=m.groups()[1]
        isl.AppendIS(t)
        return m.string[m.lastindex:]

    # And there may be a single number (maybe with trailing alpha) alone on the line
    m=Regex.match("^#?([0-9]+)([a-zA-Z]*)\s*$", islText)
    if m is not None and len(m.groups()) > 0:
        t=IssueSpec(Whole=m.groups()[0])
        t.TrailingGarbage=m.groups()[1]
        isl.AppendIS(t)
        return m.string[m.lastindex+1:]

    return ""


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Main

# Read the list of 1943 fanzines and parse them
# The format of a line is: <name> (<editor> & <editor>) >comma-separated list of issues> {comment 1} {comment 2}
# the name and editor are always present
with open("fanzines of 1943.txt") as f:
    lines=f.readlines()

lines=[l.strip() for l in lines]   # Remove whitespace including trailing '\n'

AllFanzinesFISList=[]

for line in lines:
    print("\n"+line)
    fis=FanzineSeriesSpec()

    # The line may have one or more sets of comments one or more curly brackets at the end
    notes=Regex.findall("{(.+?)}", line)    # Find all the comments
    line=Regex.sub("{(.+?)}", "", line)         # Delete all comment text by replacing them with empty strings
    if "ELIGIBLE" in notes:
        fis.Eligible=True
        notes.remove("ELIGIBLE")
    fis.Notes=notes

    m=Regex.match("(.*)\((.*)\)(.*)$", line)    # Try it without comments
    if m is not None:
        print(str(m.groups()))
    else:
        print("No match: "+line)
        continue

    fis.Name=m.groups()[0].strip()
    fis.Editor=m.groups()[1].strip()
    fis.IssueSpecList=DecodeIssueList(m.groups()[2])
    AllFanzinesFISList.append(fis)

# List the fanzines found
print("\n\n\n\n\n\n\nList of all fanzines found in list of all 1943 fanzines")
for fis in AllFanzinesFISList:
    print(fis.Format())

# OK, now it's time to read fanac.org looking for 1943 fanzines.
print("\n\n\n\n\nNow read the file of 1943 fanzines issues on fanac.org")
with open("1943 fanac.org Fanzines.txt") as f:
    lines=f.readlines()

lines=[l.strip() for l in lines]   # Remove whitespace including trailing '\n'

# The file is "||"-delimited and consists of four columns:
# Issue title (including issue number)
# Issue date
# Containing directory URL
# Issue index file name
fanacFanzinesFIDList=[]
for line in lines:
    line=line.strip()[2:-2] # Strip off outside whitespace and outside "||"
    cols=line.split("||")
    cols=[c.strip() for c in cols]

    # cols[0] should be the issue name including issue number at the end
    # We need to separate out the issue number.  It is usually the last token, but sometimes the last two tokens (e.g., V3 #4)
    fid=FanacIssueData()
    fid.DirURL=cols[2]
    fid.DisplayName=cols[0]
    fid.Filename=cols[3]

    # Now figure out the IssueSpec

    # First look for the pattern Vn[,][ ]#n where n is a number
    m=Regex.match("(.*)V([0-9]+)[, ]*#([0-9]+)$", cols[0])
    if m is not None and len(m.groups()) > 0:
        fid.IssueSpec=IssueSpec(Vol=m.groups()[1], Num=m.groups()[2])
        fid.Name=m.groups()[0]
        fanacFanzinesFIDList.append(fid)
        continue

    # Next look for the pattern #n where n is a number
    m=Regex.match("(.*) #([0-9]+)$", cols[0])
    if m is not None and len(m.groups()) > 0:
        fid.IssueSpec=IssueSpec(Whole=m.groups()[1])
        fid.Name=m.groups()[0]
        fanacFanzinesFIDList.append(fid)
        continue

    # Finally look for the pattern n where n is a number
    m=Regex.match("(.*?) ([0-9]+)$", cols[0])
    if m is not None and len(m.groups()) > 0:
        fid.IssueSpec=IssueSpec(Whole=m.groups()[1])
        fid.Name=m.groups()[0]
        fanacFanzinesFIDList.append(fid)
        continue

for fid in fanacFanzinesFIDList:
    print(fid.Format())

# Now cross-reference them.
# Go through the list of 1943 Fanzines and find those that we have on fanac.org
print("\n\n\n\nAttempt to match all fanzines published in 1943 to fanac.org 1943 fanzines")
for fis in AllFanzinesFISList:
    if fis.IssueSpecList is not None:
        for isp in fis.IssueSpecList:
            match=False
            for fid in fanacFanzinesFIDList:
                if fis.Name.lower() == fid.Name.lower():
                    if isp == fid.IssueSpec:
                        print("Match: "+fis.Name+" "+isp.Format())
                        match=True
                        break
            if not match:
                print("Failed: "+fis.Name+" "+isp.Format())

# Now the inverse: go through the 1943 fanzines we have on fanac.org and see if they're on the list of 1943 Fanzines
print("\n\n\n\nAttempt to match fanac.org's 1943 fanzines to the list of all fanzines published in 1943")
for fid in fanacFanzinesFIDList:
    match=False
    for fis in AllFanzinesFISList:
        if fis.IssueSpecList is not None:
            #print("'"+fis.Name.lower()+"'  <===>  '"+fid.Name.lower()+"'")
            if fis.Name.lower() == fid.Name.lower():
                for isp in fis.IssueSpecList:
                    #print(isp.Str()+"   <-->   "+fid.IssueSpec.Str()+"  ==> "+str(isp == fid.IssueSpec))
                    if isp == fid.IssueSpec:
                        print("Match: "+fis.Name+" "+isp.Format())
                        match=True
                        break
            if match is True:
                break
    if not match:
        print("Failed: '"+fid.Name+"'   "+fid.IssueSpec.Format())
i=0

