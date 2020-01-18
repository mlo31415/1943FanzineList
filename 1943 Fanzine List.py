import re as Regex
import os
from os import path
from FanzineIssueSpec import FanzineIssueSpec, IssueSpecList
from FanzineSeriesSpec import FanzineSeriesSpec
from FanzineIssueData import FanzineIssueData


#**************************************************************************************************************************************
# The input is text which consists of one or more FanzineIssueSpecs.
# We decode it by calling InterpretIssueSpec repeatedly until it fails to find a new FanzineIssueSpec.
# The output is an IssueSpecList
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
    #   A comma-separated list of issue whole numbers
    #   A list of Volumes and numbers (many delimiter patterns!)
    #   A range of whole numbers
    #   A list of year:issue pairs
    #  In all cases we need to be prepared to deal with (and preserve) random text.

    # Walk the issue spec decoding it as we go.
    success=True
    while success and len(issuesText) > 0:
        issuesText=issuesText.strip()  # Leading and trailing whitespace is uninteresting
        if issuesText[0] == ",":
            issuesText=issuesText[1:].strip()   # If the previous pass just took a piece of a comma-separated list, remove the leading comma and any associated whitespace
        # And try again
        iss, issuesText, success=InterpretIssueSpec(issuesText)
        isl.AppendIS(iss)

    print("   "+isl.Str())
    return isl


#.....................................
# Nibble away at a line
def MatchAndRemove(input, pattern):
    m=Regex.match(pattern, input)         # Do we match the pattern?
    if m is not None and len(m.groups()) > 0:
        g0=m.groups()[0]                    # There may be either 1 or two groups, but we need to return two matches
        g1=None
        if len(m.groups()) > 1:
            g1=m.groups()[1]
        return Regex.sub(pattern, "", input), g0, g1  # And delete the matched text
    return input, None, None
# ........................


#**************************************************************************************************************************************
# Interpret some or all of the input text (from islText) as an IssueSpecList and append the interpreted FanzineIssueSpecs we find to the input IssueSpecList, isl.
# It's permissible to not handle the complete list in one go, since we called this function repeatedly until islText is completely interpreted.
# We return a triple:
#   A IssueSpecList of one or more FanzineIssueSpecs
#   The remaining text after whatever was matched has been removed
#   True if at least one FanzineIssueSpec was found or False if none was found
def InterpretIssueSpec(islText):
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
                [#:]\s*             # Then a '#' or a ':' followed by optional whitespace
                ((?:\d+,\s*)*)      # Then a non-capturing group of one or more digits followed by a comma followed by optional whitespace
                                    # this whole thing is a group that matches all but the last of the digit-comma-[space] thingies
                (\d+[;,]?)(.*)      # Then a last group of digits which must be present followed by an optional comma followed by the rest of the line
                                    # (We rely on greedy parsing here!)
                """, Regex.X)
    m=c_VnnNnn.match(islText)
    if m is not None and len(m.groups()) == 4:
        vol=int(m.groups()[0])
        # Create iList, which is a list of issues associated with this volume number
        iList=m.groups()[1]+m.groups()[2]
        islText=m.groups()[3]
        iList=iList.replace(" ", "").replace(";", ",").split(",")  # Split on either ',' or ':'
        isl=IssueSpecList()
        for i in iList:
            if len(i) == 0:
                continue
            isl.AppendIS(FanzineIssueSpec(Vol=vol, Num=i))

        # Check to see if the last item was followed by a bracketed comment.  If so, add it to the last item.
        if len(iList) > 0:
            islText=islText.strip()
            if len(islText) > 0:
                if islText[0] == '[':
                    m=Regex.compile("^(\[.*\])(.*)$").match(islText)
                    if m is not None and len(m.groups()) == 2:
                        fis=FanzineIssueSpec()
                        fis.TrailingGarbage=m.groups()[0]
                        islText=m.groups()[1].strip()
                        if len(islText) > 0 and islText[0] == ",":
                            islText=islText[1:].strip()  # If there was a trailing comma, delete it.
                elif islText[0] == '(':
                    m=Regex.match("^(\(.*\))(.*)$", islText)
                    if m is not None and len(m.groups()) == 2:
                        fis=FanzineIssueSpec()
                        fis.TrailingGarbage=m.groups()[0]
                        islText=m.groups()[1].strip()
                        if len(islText) > 0 and islText[0] == ",":
                            islText=islText[1:].strip()  # If there was a trailing comma, delete it.

        return isl, islText, True

    # Second, deal with a range of numbers, nnn-nnn
    # Look at two cases, (1) a range all by itself and (2) A range in a list (i.e., followed by a comma)
    m=Regex.match("^(\d+)\s*[\-–]\s*(\d+)$", islText)   # First, a range all by itself
    if m is not None and len(m.groups()) == 2:
        isl=IssueSpecList()
        for k in range(int(m.groups()[0]), int(m.groups()[1])+1):
            isl.AppendIS(FanzineIssueSpec(Whole=k))
        return isl, "", True    # By definition the line is now empty

    islText, g0, g1=MatchAndRemove(islText, "^(\d+)\s*[\-–]\s*(\d+),")
    if g0 is not None and g1 is not None:
        isl=IssueSpecList()
        for k in range(int(g0), int(g1)+1):
            isl.AppendIS(FanzineIssueSpec(Whole=k))
        return isl, islText, True

    # Next, consider a list of years or year-month pairs:
    # yyyy[, yyyy]
    # yyyy:mm[, yyyy:mm]
    # The years *must* be 4-digit so we can tell them apart from just-plain-numbers
    # The months can also be text "Sep" "September" etc.
    # There are two cases, alone on the line and as part of a comma-separated list
    # Year alone
    patterns=["^(\d{4}):(\d{1,2})\s*,", # Year:month comma-terminated
              "^(\d{4}):(\d{1,2})",     # Year:month
              "^(\d{4}):([a-zA-Z]+),",  # Year:textmonth comma-terminated
              "^(\d{4}):([a-zA-Z]+)",   # Year:textmonth
              "^(\d{4})\s*,",  # Year comma-terminated
              "^(\d{4})",  # Year
              ]
    for pat in patterns:
        islText, t1, t2=MatchAndRemove(islText, pat)
        if t1 is not None:
            isl=IssueSpecList().AppendIS(FanzineIssueSpec().SetDate(t1, t2))
            return isl, islText, True

    # Now consider it as a simple list of whole numbers with a trailing alphabetic character (e.g, 24, 25, 25A, 26) (and perhaps with a # in front of the number, e.g., #2)
    # So we want to match <optional whitespace><digits><optional alphas><optional whitespace><comma>
    patterns=["^#?([0-9]+)([a-zA-Z])\s*,",  # <Integer>[alpha]<comma>
              "^#?([0-9]+\.[0-9]+)([a-zA-Z])\s*,",  # <Decimal>[alpha]<comma>
              "^#?([0-9]+)([a-zA-Z])\s*$",  # <Integer>[alpha] (if there's no comma, then we need to see line-end)
              "^#?([0-9]+\.[0-9]+)([a-zA-Z])\s*$"  # <Decimal>[alpha] (if there's no comma, then we need to see line-end)
              ]
    for pat in patterns:
        islText, t1, t2=MatchAndRemove(islText, pat)
        if t1 is not None:
            fis=FanzineIssueSpec(Whole=t1)
            fis.TrailingGarbage=t2
            isl=IssueSpecList(List=fis)
            return isl, islText, True

    # Finally consider it as a simple list of whole numbers with no trailing alphabetics (and perhaps with a # in front of the number, e.g., #2)
    # So we want to match <optional whitespace><digits><optional alphas><optional whitespace><comma>
    patterns=["^#?([0-9]+)\s*,",         # <Integer><comma>
              "^#?([0-9]+\.[0-9]+)\s*,", # <Decimal><comma>
              "^#?([0-9]+)\s*$",          # <Integer> (if there's no comma, then we need to see line-end)
              "^#?([0-9]+\.[0-9]+)\s*$"   # <Decimal> (if there's no comma, then we need to see line-end)
              ]
    for pat in patterns:
        islText, t1, t2=MatchAndRemove(islText, pat)
        if t1 is not None:
            fis=FanzineIssueSpec(Whole=t1)
            fis.TrailingGarbage=t2
            isl=IssueSpecList(List=fis)
            return isl, islText, True

    return None, islText, False


#**************************************************************************************************************************************
import collections
def ReadExternalLinks(filename):
    externalLinks=[]
    print("\n\n----Begin reading "+filename)
    # Now we read Links1942.txt, which contains links to issues of fanzines *outside* fanac.org.
    # It is organized as a table, with the first row a ';'-delimited list of column headers
    #    and the remaining rows are each a ';'-delimited pointer to an exteral fanzine
    # First read the header line which names the columns.  The headers are separated from ';", so we need to remove these.
    if not os.path.exists(filename):
        print("ReadExternalLinks: "+filename+" not found.")
        return []
    with open(filename) as f:
        lines=f.readlines()
    lines=[l.strip() for l in lines]  # Remove whitespace including trailing '\n'
    line=lines[0].replace(";", "")
    del lines[0]
    externalLinksColNames=line.split(" ")
    # The columns are labeled: Title; Issue; Editor; Volume; Number; Whole_Number; Month; Day; Year; URL
    # We need Title, Volume, Number, Whole, Issue, and URL
    cName=externalLinksColNames.index("Title") # (Title is really the series name)
    cDisplayName=externalLinksColNames.index("Issue")   # (Issue is really the display name)
    cVol=externalLinksColNames.index("Volume")
    cNum=externalLinksColNames.index("Number")
    cWhole=externalLinksColNames.index("Whole_Number")
    cURL=externalLinksColNames.index("URL")

    # Now read the rest of the data.
    # It's a series of lines, each of which is ten ';'-separated fields
    for line in lines:  # Each remaining line is a link to an external fanzine
        line=line.strip()
        if len(line) == 0:      # Skip empty lines
            continue
        if line[0] == "#":
            continue            # Skip comment lines
        print("   line="+line)
        t2=[t.strip() for t in line.split(";")]
        if len(t2) != 10:       # There should be exactly ten items in each line
            print("***External fanzine link length error: Length should be 10 but is "+str(len(t2)))
            continue
        fis=FanzineIssueSpec(Num=t2[cNum], Vol=t2[cVol], Whole=t2[cWhole])
        elFID=FanzineIssueData(URL=t2[cURL], SeriesName=t2[cName], DisplayName=t2[cDisplayName], FanzineIssueSpec=fis)
        externalLinks.append(elFID)
    print("----Done reading "+filename)
    return externalLinks


#**************************************************************************************************************************************
# Read the master file of all fanzines for the specified year
def ReadAllYearsFanzines(name):
    # Read the list of the year's fanzines and parse them
    # The format of a line is: <series name> (<editor> [& <editor>...]) >comma-separated list of issues> {comment 1} {comment 2}
    # the name and editor are always present
    with open(name) as f:
        lines=f.readlines()
    lines=[l.strip() for l in lines]  # Remove whitespace including trailing '\n'
    # Ignore all lines beginning with "#"
    lines=[l for l in lines if not (len(l) > 0 and l[0] == "#") ]
    allFanzinesFSSList=[]
    for line in lines:
        print("\n"+line)
        fss=FanzineSeriesSpec()

        # The line may have one or more sets of comments one or more curly brackets at the end
        # Begin by recognizing them and removingt hem from the line
        notes=Regex.findall("{(.+?)}", line)  # Find all the comments
        line=Regex.sub("{(.+?)}", "", line)   # Delete all comment text by replacing them with empty strings
        if "ELIGIBLE" in notes:               # "ELIGIBLE" is a special case and means that it's eligible for the Retro Hugo for fanzines.  We store that flag separately.
            fss.Eligible=True
            notes.remove("ELIGIBLE")
        fss.Notes=notes

        # Now there are no comments, so the line's format is <series name> (<editor> [& <editor>...]) <comma-separated list of issuespecs>
        # the series name and editor is mandatory; the issuespecs are not when the fanzine is a one-shot
        m=Regex.match("(.*)\((.*)\)(.*)$", line)    # We're using the parenthesis around the editor(s) to delimit the three sections of the line.
        if m is None:
            print("No match: "+line)
            continue
        print(str(m.groups()))

        # Decode and store the data.
        fss.SeriesName=m.groups()[0].strip()
        fss.Editor=m.groups()[1].strip()
        fss.IssueSpecList=DecodeIssueList(m.groups()[2])
        allFanzinesFSSList.append(fss)

    # List the fanzines found (a debugging aid)
    print("\n\n\n\n\n\n\nList of all fanzines found in list of all "+theYear+" fanzines")
    for fss in allFanzinesFSSList:
        print(fss.Format())

    return allFanzinesFSSList


#**************************************************************************************************************
def ReadFanacFanzines(name):
    print("\n\n\n\n\nNow read the file of "+theYear+" fanzines issues on fanac.org")
    with open(name) as f:
        lines=f.readlines()
    lines=[l.strip() for l in lines]  # Remove whitespace including trailing '\n'

    # The file is "||"-delimited and consists of four columns:
    # Issue title (including issue number)
    # Issue date
    # Containing directory URL
    # Issue index file name
    fanzinesFIDList=[]
    for line in lines:
        line=line.strip()[2:-2]  # Strip off outside whitespace and outside "||"
        if len(line) == 0:  # Skip whitespace lines
            continue
        cols=line.split("||")
        cols=[c.strip() for c in cols]

        # cols[0] should be the issue name including issue number at the end
        # We need to separate out the issue number.  It is usually the last token, but sometimes the last two tokens (e.g., V3 #4)
        issueName=cols[0]

        # Now figure out the FanzineIssueSpec.
        # We (try to) do this by splitting the issue spec off from the series name which it normally follows
        # Typically, it will be a <bunch of stuff><whitespace><issue spec>
        # Our strategy will be to break the issueName into tokens on whitespace, and work backwards from the end, concatenating until we fail to recognize an issue spec
        # This lets us use the existing issue spec recognizer.

        tokens=issueName.split()
        isl=IssueSpecList()
        # Try to greedily interpret the trailing text as a FanzineIssueSpec.
        # We do this by interpreting more and more tokens starting from the end until we have something that is no longer recognizable as a FanzineIssueSpec
        # The just-previous set of tokens constitutes the full IssueSpec, and the remaining leading tokens are the series name.
        for index in range(len(tokens)-1, -1, -1):  # Ugly, but I need index to be the indexes of the tokens
            trailingText=" ".join(tokens[index:])
            leadingText=" ".join(tokens[:index])
            print("     index="+str(index)+"'   leading='"+leadingText+"    trailing='"+trailingText+"'")
            trialIsl, leftover, success=InterpretIssueSpec(trailingText)
            if not success:       # Failed.  We've gone one too far. Quit trying and use what we found on the previous iteration
                print("      ...failed. ISL="+isl.Str())
                break
            isl=trialIsl
            goodLeadingText=leadingText

        if len(isl) == 0:
            fid=FanzineIssueData(DisplayName=issueName, URL=cols[2]+"/"+cols[3], SeriesName=issueName, FanzineIssueSpec=FanzineIssueSpec())
            fanzinesFIDList.append(fid)
            print(fid.Format())
        else:
            for i in isl:
                fid=FanzineIssueData(DisplayName=issueName, URL=cols[2]+"/"+cols[3], SeriesName=goodLeadingText, FanzineIssueSpec=i)
                fanzinesFIDList.append(fid)
                print(fid.Format())

    return fanzinesFIDList


#..........................................
def NamesMatch(name1, name2):
    if name1 is None and name2 is None:
        return True
    if name1 is not None and name2 is not None and name1.lower() == name2.lower():
        return True
    return False

def StrNone(str):
    if str is None:
        return "<None>"
    return str

#...........................................
# Locate an fid in the all fanzines FSS list
# Return with None or the fss matched
def FindInFSSList(fssList, fid):
    for fss in fssList:
        if fss.IssueSpecList is not None:
            if NamesMatch(fss.SeriesName, fid.SeriesName):
                for isp in fss.IssueSpecList:
                    if isp == fid.FanzineIssueSpec:
                        print("'"+StrNone(fss.SeriesName).lower()+"'  <===>  '"+StrNone(fid.SeriesName).lower()+"'")
                        print(StrNone(isp.Str())+"   <-->   "+StrNone(fid.FanzineIssueSpec.Str())+"  ==> "+str(isp == fid.FanzineIssueSpec))
                        print("Match: "+fss.SeriesName+" "+isp.Format())
                        return fss
    print("Failed: '"+fid.DisplayName+"'")
    return None

#........................
def LookupFSS(fssToFID, fss, iss):
    if fss.SeriesName not in fssToFID.keys():
        return None
    for x in fssToFID[fss.SeriesName]:
        if x[0] == iss:
            return x[1]
    return None
#........................
def LookupURLFromName(fidList, name):
    urllist=[f for f in fidList if f.SeriesName == name] # List of all fanac.org FID entries with this name
    if urllist == None or len(urllist) == 0:
        return None
    # Need to remove filename to get just path
    return path.split(urllist[0].URL)[0]
#........................



#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Main

theYear="1944"

# Read the master list of all the year's fanzines
allFanzinesFSSList=ReadAllYearsFanzines(theYear+" All Fanzines list.txt")

# Read what's on fanac.org
fanzinesFIDList=ReadFanacFanzines(theYear+" Fanac.org Fanzines.txt")

for fid in fanzinesFIDList:
    print(fid.Format())

# Now cross-reference them.
# First go through the the years fanzines we have on fanac.org and see if they're on the list of all the year's Fanzines
# For each one that is, add a tuple to
print("\n\n\n\nAttempt to match fanac.org's "+theYear+" fanzines to the list of all fanzines published in "+theYear+"")

# Next, we read in the list of "foreign" fanzine links and append it to the list from fanac.org
fanzinesFIDList.extend(ReadExternalLinks(theYear+" External Fanzine Links.txt"))

# Build a dictionary of matches between FIDs in fanac.org and elsewhere and FSSs in the list of all the year's fanzines
# Create a dictionary keyed by fanzine name. The value is a dictionary keyed by FanzineIssueSpec names.  The value of *those* is the IssueData for the link we need
fssToFID={}
for fid in fanzinesFIDList:
    fss=FindInFSSList(allFanzinesFSSList, fid)
    if fss is not None:
        lst=fssToFID.get(fid.SeriesName)    # Get a list of (issue spec, fid) tuples
        if lst is None:
            lst=[]
        lst.append((fid.FanzineIssueSpec, fid))     # And append a final tuple which
        fssToFID[fid.SeriesName]=lst

# Sort allFanzinesFSSList into alphabetic order
# We move A, An and The to the end for sorting purposes
def inverter(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix):]+s[:len(prefix)]
    return s
def sorter(fss):
    s=fss.SeriesName
    s=s.lower()
    s=inverter(s, "a ")
    s=inverter(s, "an ")
    s=inverter(s, "the ")
    return s

allFanzinesFSSList.sort(key=sorter)


#============================================================================================
# Write the HTML
#============================================================================================
print("----Begin generating the HTML")
f=open(theYear+".html", "w")
f.write('<!doctype html>\n')
f.write('<html lang="en">\n')
f.write('\n')
f.write('<head>\n')
f.write('  <!-- Required meta tags -->\n')
f.write('  <meta charset="utf-8">\n')
f.write('  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">\n')
f.write('\n')
f.write('  <!-- Bootstrap CSS -->\n')
f.write('  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"\n')
f.write('    integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">\n')
f.write('\n')
f.write('    <style>\n')
f.write('      .narrowLeft {\n')
f.write('        max-width: 900px;\n')
f.write('        margin-left: 10px\n')
f.write('        }\n')
f.write('    </style>\n')
f.write('	 <style>\n')
f.write('	     a:link {color: Blue}\n')
f.write('    </style>\n')
f.write('    <style>\n')
f.write('        ul {line-height:130%}\n')
f.write('    </style>\n')
f.write('<title>'+theYear+' Fanzines and the Retro Hugos\n')
f.write('</title></head\n')
f.write("<body>\n")
f.write('<style>\n')
f.write('<!--\n')
f.write('p            { line-height: 100%; margin-top: 0; margin-bottom: 0 }\n')
f.write('-->\n')
f.write('</style>\n')
f.write('<div  class="container narrowLeft">\n')
f.write('<h3><center>'+theYear+' Fanzines and the Retro Hugos</center></h3>\n')

f.write("<h6>The 2019 Worldcon, Dublin 2019, will award the 2019 Retro Hugos for works published in 1943. <p>Here is the list of fanzines from that year, with links to the issues available on-line.  This list will be updated as we are able to get more 1943 fanzines on-line, so keep checking! </p>We hope that having access to the original source material will help nominators to select worthy candidates for the Retro Fanzine, Fan Writer and Fan Artist awards.</h6>")
f.write('<div class="row border">\n')
f.write('   <div class=col-md-6>\n')
f.write('      <ul>')

# We want to produce a two-column page, with well-balanced columns. Count the number of distinct title (not issues) in allFanzines1942 so we can put half in each column
listoftitles=set()
for fss in allFanzinesFSSList:  # fz is a FanzineSeriesSpec class object
    listoftitles.add(fss.SeriesName)
numTitles=len(listoftitles)

#........................
def FormatLink(name, url):
    return '<a href='+url+'>'+name+'</a>'
#........................
def FormatISSListAsHtml(issList, fidList):
    s=""
    for iss, fid in zip(issList, fidList):
        if len(s) > 0:
            s=s+", &nbsp;&nbsp;&nbsp;"
        if fid is None:
            s=s+iss.Format()
        else:
            s=s+FormatLink(iss.Format(), fid.URL)
    return s
#........................


# Create the HTML table rows
listoftitles=[]     # Empty it so we can again add titles to it as we find them
for fz in allFanzinesFSSList:  # fz is a FanzineSeriesSpec class object
    print("   Writing HTML for: "+fz.Str())

    htm=None
    name=fz.SeriesName
    editors=fz.Editor

    # There are three cases:
    #   Case 1: We have online copies of one or more the year's issues for this fanzine
    #   Case 2: We don't have any of the year's issue online, but we do have issues from other years
    #   Case 3: We have no issues at all from this fanzine

    # Create a list of FIDs to parallel the fanzine's ISS list.
    # Determine if any were found
    fidList=None
    if fz.IssueSpecList is not None:
        fidList=[]
        for iss in fz.IssueSpecList:
            fidList.append(LookupFSS(fssToFID, fz, iss))   # Create a list of FIDs corresponding to the ISS list in fz.  Some or all will be None.

    issHtml=""
    if fz.IssueSpecList is not None:
        issHtml=FormatISSListAsHtml(fz.IssueSpecList, fidList)

    seriesURL=LookupURLFromName(fanzinesFIDList, fz.SeriesName)
    htm="<i>"
    if seriesURL is not None:
        htm=htm+FormatLink(name, seriesURL)
    else:
        htm=htm+name
    htm=htm+"</i>&nbsp;&nbsp;("+editors+")"
    if fz.Notes is not None:
        for note in fz.Notes:
            htm=htm+" {<i>"+note+"</i>}"
    if fz.Eligible:
        htm=htm+'<font color="#FF0000">&nbsp;&nbsp;(Eligible)</font>&nbsp;&nbsp;'
    htm=htm+"<br>"+issHtml

    # Insert the column end, new column start HTML when half the fanzines titles have been processed.
    if not fz.SeriesName in listoftitles:
        listoftitles.append(fz.SeriesName)
    if round(numTitles/2) == len(listoftitles):
        f.write('      </ul>')
        f.write('   </div>\n')
        f.write('   <div class=col-md-6>\n')
        f.write('      <ul>')

    if htm is not None:
        print(htm)
        f.write("   <li>"+htm+'\n')

# And finally the table end and page end code
f.write('      </ul>')
f.write('   </div>\n')
f.write('</div>\n')
f.write('<center>Scanning by Joe Siclari and Mark Olson</p></center>')
f.write('</ul></body>')
f.flush()
f.close()

i=0

