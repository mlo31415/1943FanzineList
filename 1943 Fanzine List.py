import re as Regex
import os
from os import path
from FanzineIssueSpec import FanzineIssueSpec
from FanzineIssueSpecList import FanzineIssueSpecList
from FanzineSeriesSpec import FanzineSeriesSpec
from FanzineIssueData import FanzineIssueData
from Helpers import ToNumeric


#**************************************************************************************************************************************
# The input is text which consists of one or more FanzineIssueSpecs.
# We decode it by calling InterpretIssueSpec repeatedly until it fails to find a new FanzineIssueSpec.
# The output is an IssueSpecList
def DecodeIssueList(issuesText):
    if issuesText is None:    # Skip empty stuff
        return None
    if len(issuesText.strip()) == 0: # Skip if it's all whitespace
        return None

    # Turn all multiple spaces into a single space. (Split splits on whitespace; then rejoin fragments with single space; This also strips line.)
    issuesText=' '.join(issuesText.split())

    # Create am empty IssueSpecList
    isl=FanzineIssueSpecList()   # This will be the list of IssueSpecs resulting from interpreting issuesText

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

    print("   "+isl.DebugStr())
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
        isl=FanzineIssueSpecList()
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
        isl=FanzineIssueSpecList()
        for k in range(int(m.groups()[0]), int(m.groups()[1])+1):
            isl.AppendIS(FanzineIssueSpec(Whole=k))
        return isl, "", True    # By definition the line is now empty

    islText, g0, g1=MatchAndRemove(islText, "^(\d+)\s*[\-–]\s*(\d+),")
    if g0 is not None and g1 is not None:
        isl=FanzineIssueSpecList()
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
            isl=FanzineIssueSpecList().AppendIS(FanzineIssueSpec().SetDate(t1, t2))
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
            fis=FanzineIssueSpec().SetWhole(t1, t2)
            isl=FanzineIssueSpecList(List=fis)
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
            fis=FanzineIssueSpec().SetWhole(t1, t2)
            isl=FanzineIssueSpecList(List=fis)
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
        # Create the FIS and FID and append it to the external links list
        fis=FanzineIssueSpec(Num=ToNumeric(t2[cNum]), Vol=ToNumeric(t2[cVol]), Whole=ToNumeric(t2[cWhole]))
        elFID=FanzineIssueData(URL=t2[cURL], SeriesName=t2[cName], DisplayName=t2[cDisplayName], FanzineIssueSpec=fis)
        externalLinks.append(elFID)
    print("----Done reading "+filename)
    return externalLinks


#**************************************************************************************************************************************
# Read the master file of all fanzines for the specified year
def ReadAllYearsFanzines(name):

    # Read the contents of the file and strip leading and traling whitespace
    with open(name) as f:
        lines=f.readlines()
    lines=[l.strip() for l in lines]  # Remove whitespace including trailing '\n'

    # Look for a block of text that begins "<top matter" and ends "</top matter>".  This will be the header of the HTML file
    # "<top matter"> begins a line, and "</top matter>" ends a subsequent line
    # Once we've located the top matter, weeliminate those lines from further processing.for i in range(0, len(lines)
    start=None
    end=None
    for i in range(0, len(lines)):
        if lines[i].startswith("<top matter>"):
            start=i
        if lines[i].endswith("</top matter>"):
            end=i
    topmatter=None
    if start is not None and end is not None and start <= end:
        topmatter=lines[start:end+1]
        topmatter=" ".join(topmatter)
        topmatter=topmatter[12:-13]
        del lines[start:end+1]

    # The format of a line is: <series name> (<editor> [& <editor>...]) >comma-separated list of issues> {comment 1} {comment 2}
    # the name and editor are always present
    # Ignore all lines beginning with "#"
    lines=[l for l in lines if not (len(l) > 0 and l[0] == "#") ]
    allFanzinesFSSList=[]
    for line in lines:
        if len(line.strip()) == 0:
            continue;
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
            print("****No match: "+line)
            continue
        print(str(m.groups()))

        # Decode and store the data.
        fss.SeriesName=m.groups()[0].strip()
        fss.Editor=m.groups()[1].strip()
        fss.FanzineIssueSpecList=DecodeIssueList(m.groups()[2])
        allFanzinesFSSList.append(fss)

    # List the fanzines found (a debugging aid)
    print("\n\n\n\n\n\n\nList of all fanzines found in list of all "+theYear+" fanzines")
    for fss in allFanzinesFSSList:
        print(str(fss))

    return allFanzinesFSSList, topmatter


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
        isl=FanzineIssueSpecList() # This is a list of ISLs that we have found.
        # Try to greedily interpret the trailing text as a FanzineIssueSpec.
        # We do this by interpreting more and more tokens starting from the end until we have something that is no longer recognizable as a FanzineIssueSpec
        # The just-previous set of tokens constitutes the full IssueSpec, and the remaining leading tokens are the series name.
        for index in range(len(tokens)-1, -1, -1):  # Ugly, but I need index to be the indexes of the tokens
            trailingText=" ".join(tokens[index:])
            leadingText=" ".join(tokens[:index])
            print("     index="+str(index)+"   leading='"+leadingText+"'    trailing='"+trailingText+"'")
            trialIsl, leftover, success=InterpretIssueSpec(trailingText)
            if not success:       # Failed.  We've gone one too far. Quit trying and use what we found on the previous iteration
                print("     ...backtracking. ISL="+isl.DebugStr())
                break
            isl=trialIsl
            goodLeadingText=leadingText

        if len(isl) == 0:
            print("     no issue number found")
            fid=FanzineIssueData(DisplayName=issueName, URL=cols[2]+"/"+cols[3], SeriesName=issueName, FanzineIssueSpec=FanzineIssueSpec(), Fanac=True)
            fanzinesFIDList.append(fid)
            print(str(fid))
        else:
            if len(isl) > 1:    # This happens when an ISL is something like "4-7"
                print("     "+str(len(isl))+" ISLs found")
            for i in isl:
                fid=FanzineIssueData(DisplayName=issueName, URL=cols[2]+"/"+cols[3], SeriesName=goodLeadingText, FanzineIssueSpec=i, Fanac=True)
                fanzinesFIDList.append(fid)
                print(str(fid))

        print("")

    return fanzinesFIDList


#..........................................
def NamesMatch(name1, name2):
    if name1 is None and name2 is None:
        return True
    if name1 is None or name2 is None:
        return False
    name1=name1.lower()
    if name1.startswith("the "):
        name1=name1[4:]+", the"
    name2=name2.lower()
    if name2.startswith("the "):
        name2=name2[4:]+", the"
    if name1 == name2:
        return True
    return False


#........................
def LookupURLFromName(fidList, name):
    urllist=[f for f in fidList if f.SeriesName == name] # List of all fanac.org FID entries with this name
    if urllist == None or len(urllist) == 0:
        return None
    # Need to remove filename to get just path
    return path.split(urllist[0].URL)[0]
#........................


##############################################################################
##############################################################################
###############################  Main  #######################################
##############################################################################

theYear="1944"

# Read the master list of all the year's fanzines
print("\nRead "+theYear+"'s master list of all fanzines published\n")
allYearsFanzinesFSSList, topmatter=ReadAllYearsFanzines(theYear+" All Fanzines list.txt")

# Read what's on fanac.org
print("\nRead what's on fanac.org for "+theYear+"\n")
fanacFanzines=ReadFanacFanzines(theYear+" Fanac.org Fanzines.txt")
allKnownIssuesFIDList=fanacFanzines

for fid in allKnownIssuesFIDList:
    print(str(fid))

# Next, we read in the list of "foreign" fanzine links and append it to the list from fanac.org
allKnownIssuesFIDList.extend(ReadExternalLinks(theYear+" External Fanzine Links.txt"))

# Sort allFanzinesFSSList into alphabetic order.
# We move A, An and The to the end for sorting purposes.
# (These two functions are used only in the sort.)
def inverter(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix):]+s[:len(prefix)]
    return s
def sorter(fss):
    s=fss.SeriesName.lower()
    s=inverter(s, "a ")
    s=inverter(s, "an ")
    s=inverter(s, "the ")
    return s

allYearsFanzinesFSSList.sort(key=sorter)


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
if topmatter is not None:
    f.write(topmatter+"\n")
f.write('<div class="row border">\n')
f.write('   <div class=col-md-6>\n')
f.write('      <ul>\n')

# We want to produce a two-column page, with well-balanced columns.
# Count the number of distinct title (not issues) in allFanzines1942 so we can put half in each column
setoftitles=set()
for fss in allYearsFanzinesFSSList:  # fz is a FanzineSeriesSpec class object
    setoftitles.add(fss.SeriesName)
numTitles=len(setoftitles)

# Create the HTML table rows
countOfTitlesInCol=0    # We want to put the first half of the fanzines in column 1 and the rest in col 2.  We need to know when to switch cols.
for fz in allYearsFanzinesFSSList:  # fz is a FanzineSeriesSpec class object
    print("   Writing HTML for: "+fz.DebugStr())

    name=fz.SeriesName
    editors=fz.Editor

    # The first thing to generate in the line containing the fanzine name -- the SeriesSpec.
    # But, there's a complication: If the fanzine is a one-off, there's probably no issue list.
    # If there is no issue list, the fanzine name links directly to the issue;
    # If there *is* an issue list, and it's a fanac.org fanzine, the fanzine name links to the series index page and
    # the issue list links to the individual issues
    seriesURL=LookupURLFromName(allKnownIssuesFIDList, fz.SeriesName)
    htm="<i>"
    if fz.FanzineIssueSpecList is not None:
        if seriesURL is not None:
            htm+='<a href='+seriesURL+'>'+name+'</a>'
        else:
            htm+=name
    else:
        newHtml=None
        for fidInAll in allKnownIssuesFIDList:
            if NamesMatch(fz.SeriesName, fidInAll.SeriesName) and fidInAll.FanzineIssueSpec == isl:
                newHtml='<a href='+fidInAll.URL+'>'+name+'</a>'
        if newHtml is None:
            newHtml=name
        htm+=newHtml
    htm+="</i>&nbsp;&nbsp;("+editors+")"

    if fz.Notes is not None:
        for note in fz.Notes:
            htm+=" {<i>"+note+"</i>}"

    if fz.Eligible:
        htm+='<font color="#FF0000">&nbsp;&nbsp;(Eligible)</font>&nbsp;&nbsp;'

    # There are three cases:
    #   Case 1: We have online copies of one or more the year's issues for this fanzine
    #   Case 2: We don't have any of the year's issue online, but we do have issues from other years
    #   Case 3: We have no issues at all from this fanzine
    issHtml=""
    if fz.FanzineIssueSpecList is not None:
        for isl in fz.FanzineIssueSpecList:
            if len(issHtml) > 0:
                issHtml+=", &nbsp;&nbsp;&nbsp;"
            # Find the entry in all known issues where the seriesName and iss match
            newHtml=str(isl)
            for fidInAll in allKnownIssuesFIDList:
                if NamesMatch(fz.SeriesName, fidInAll.SeriesName) and fidInAll.FanzineIssueSpec == isl:
                    newHtml='<a href='+fidInAll.URL+'>'+str(isl)+'</a>'
                    break
            issHtml+=newHtml

    htm=htm+"<br>"+issHtml

    # When half the fanzines titles have been processed, insert the column end, new column start HTML
    countOfTitlesInCol+=1
    if countOfTitlesInCol == round(numTitles/2):
        f.write('      </ul>')
        f.write('   </div>\n')
        f.write('   <div class=col-md-6>\n')
        f.write('      <ul>')

    if htm is not None:
        print(htm)
        f.write("   <li>"+htm+'\n')

# And finally the table end and page end code
f.write('      </ul>\n')
f.write('   </div>\n')
f.write('</div>\n')
f.write('<center>Scanning by Joe Siclari and Mark Olson</p></center>\n')
f.write('</ul></body>')
f.flush()
f.close()

i=0

