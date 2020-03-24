import os
import re as Regex
from os import path
from time import localtime, strftime
from typing import List, Tuple, Optional

from HelpersPackage import FormatLink
from HelpersPackage import CompareTitles

from Log import LogOpen, Log

from FanzineIssueSpecPackage import FanzineIssueInfo, FanzineDate, FanzineIssueSpec, FanzineIssueSpecList
from FanzineSeriesSpec import FanzineSeriesSpec


#**************************************************************************************************************************************
def ReadExternalLinks(filename: str) -> List[FanzineIssueInfo]:
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
        print("   external="+line)
        t2=[t.strip() for t in line.split(";")]
        if len(t2) != 10:       # There should be exactly ten items in each line
            print("***External fanzine link length error: Length should be 10 but is "+str(len(t2)))
            continue
        # Create the FIS and FID and append it to the external links list
        fis=FanzineIssueSpec(Num=t2[cNum], Vol=t2[cVol], Whole=t2[cWhole])
        fid=FanzineIssueInfo(URL=t2[cURL], SeriesName=t2[cName], DisplayName=t2[cDisplayName], FIS=fis)
        print("   "+str(fid))
        externalLinks.append(fid)
    print("----Done reading "+filename)
    return externalLinks


#**************************************************************************************************************************************
# Read the master file of all fanzines for the specified year
def ReadAllYearsFanzines(name: str) -> Tuple[List[FanzineSeriesSpec], str]:

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
            continue
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
        fisl=FanzineIssueSpecList().Match(m.groups()[2])
        if not fisl.IsEmpty():
            fss.FISL=fisl

        Log("   " +str(fss))
        allFanzinesFSSList.append(fss)

    # List the fanzines found (a debugging aid)
    print("\n\n\n\n\n\n\nList of all fanzines found in list of all "+theYear+" fanzines")
    for fss in allFanzinesFSSList:
        print(str(fss))

    return allFanzinesFSSList, topmatter


#**************************************************************************************************************
def ReadFanacFanzines(name: str) -> List[FanzineIssueInfo]:
    print("\nNow read the file of "+theYear+" fanzines issues on fanac.org")
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
        fisl, therest=FanzineIssueSpecList().GetTrailingSerial(issueName)
        if fisl is None:
            print("     no issue number found")
            fid=FanzineIssueInfo(DisplayName=issueName, URL=cols[2]+"/"+cols[3], SeriesName=issueName, FIS=FanzineIssueSpec())
            fanzinesFIDList.append(fid)
            print(str(fid))
        else:
            if len(fisl) > 1:    # This happens when an FISL is something like "4-7"
                print("     "+str(len(fisl))+" FISLs found")
            for i in fisl:
                fid=FanzineIssueInfo(DisplayName=issueName, URL=cols[2]+"/"+cols[3], SeriesName=therest, FIS=i)
                fanzinesFIDList.append(fid)
                print(str(fid))

        print("")

    return fanzinesFIDList



##############################################################################
##############################################################################
###############################  Main  #######################################
##############################################################################

theYear="1944"
LogOpen("Log -- Annual Fanzine List.txt", "Log (Errors) -- Annual Fanzine List.txt")

# Read the master list of all the year's fanzines
print("\nRead "+theYear+"'s master list of all fanzines published\n")
allYearsFanzinesFSSList, topmatter=ReadAllYearsFanzines(theYear+" All Fanzines list.txt")

# Read what's on fanac.org
fanacFanzines=ReadFanacFanzines(theYear+" Fanac.org Fanzines.txt")

# For Fanac fanzines (and for Fanac fanzines only) fill in the series URL in the FSS
for fz in allYearsFanzinesFSSList:
    seriesName=fz.SeriesName
    for ff in fanacFanzines:
        if CompareTitles(seriesName, ff.SeriesName):
            if ff.URL is not None and len(ff.URL) > 0:
                fz.SeriesURL=path.split(ff.URL)[0]            # Need to remove filename to get just path

allKnownIssuesFIDList=fanacFanzines

for fid in allKnownIssuesFIDList:
    print("allKnownIssuesFIDList: "+str(fid))

# Next, we read in the list of "foreign" fanzine links and append it to the list from fanac.org
allKnownIssuesFIDList.extend(ReadExternalLinks(theYear+" External Fanzine Links.txt"))

# Sort allFanzinesFSSList into alphabetic order.
# We move A, An and The to the end for sorting purposes.
# (These two functions are used only in the sort.)
def inverter(s, prefix: str) -> str:
    if s.startswith(prefix):
        return s[len(prefix):]+s[:len(prefix)]
    return s
def sorter(fss: FanzineSeriesSpec) -> str:
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
f.write('<div class="container narrowLeft">\n')
f.write('<a href="http://www.fanac.org/" class="btn btn-info" role="button">Fanac.org Home</a>\n')
f.write('<a href="http://fanac.org/fanzines/Classic_Fanzines.html" class="btn btn-info" role="button">Fanzines</a>\n')
f.write('<div  class="container narrowLeft">\n')
f.write('<h3><center>'+theYear+' Fanzines and the Retro Hugos</center></h3>\n')
if topmatter is not None:
    f.write(topmatter+"\n")
f.write("Indexed as of "+strftime("%Y-%m-%d %H:%M:%S", localtime())+" EST")
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
# Get a pretty good estimate of the number of lines in the table. This will be used to balance the two columns.
def EstSize(fz: FanzineSeriesSpec) -> int:
    estimatedCountOfLines=1
    if fz.LenFISL() > 0 and len(fz.FISL) >= 9:
        estimatedCountOfLines+=len(fz.FISL)/9
    return estimatedCountOfLines

estimatedCountOfLines=0
for fz in allYearsFanzinesFSSList:
    estimatedCountOfLines+=EstSize(fz)

# Now generate the table
countOfTitlesInCol=0    # We want to put the first half of the fanzines in column 1 and the rest in col 2.  We need to know when to switch cols.
for fz in allYearsFanzinesFSSList:  # fz is a FanzineSeriesSpec class object
    print("   Writing HTML for: "+fz.DebugStr())

    name=fz.SeriesName
    editors=fz.Editor

    # The first thing to generate in the line containing the fanzine name -- the SeriesSpec.
    # But, there's a complication: If the fanzine is a one-off, there's probably no issue list.
    # If there is no issue list, the fanzine name links directly to the issue;
    # If there *is* an issue list, and the FSS has a series URL, the fanzine name links to the series URL page and
    #    the issue list links to the individual issues
    # There's a third case (which seems rare) where there is no issue list, but the fanzine is on an index page with a series name which differs
    #    E.g., Tucker's "1943 Fanzine Yearbook" is a one-off which is listed as part of Le Zombie, and there's no issue number
    #    The issue needs to be linked to the fanzine name.
    # For now, we're going to ignore it and just let the name link to the index page.
    #TODO: Deal with this, maybe?
    htm="<i>"
    if fz.LenFISL() > 0:
        if fz.SeriesURL is not "":
            htm+=FormatLink(fz.SeriesURL, name)
        else:
            htm+=name
    else:
        newHtml=None
        if fz.SeriesURL is not None and len(fz.SeriesURL) > 0:
            newHtml=FormatLink(fz.SeriesURL, name)
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
    #   Case 1: We have online copies of one or more of the year's issues for this fanzine
    #   Case 2: We don't have any of the year's issue online, but we do have issues from other years
    #   Case 3: We have no issues at all from this fanzine
    fislhtml=""
    if fz.FISL is not None:
        for fis in fz.FISL:
            if len(fislhtml) > 0:
                fislhtml+=", &nbsp;&nbsp;&nbsp;"
            # Find the entry in all known issues where the seriesName and iss match
            newHtml=str(fis)
            for fidInAll in allKnownIssuesFIDList:
                if CompareTitles(fz.SeriesName, fidInAll.SeriesName):
                    print("     "+fidInAll.FIS.DebugStr()+"  == "+fis.DebugStr()+"   -> "+str(fidInAll.FIS == fis))
                if CompareTitles(fz.SeriesName, fidInAll.SeriesName) and fidInAll.FIS == fis:
                    newHtml=FormatLink(fidInAll.URL, str(fis))
                    break
            fislhtml+=newHtml

    htm=htm+"<br>"+fislhtml

    # When half the fanzines titles have been processed, insert the column end, new column start HTML
    countOfTitlesInCol+=EstSize(fz)

    if estimatedCountOfLines != -1 and  countOfTitlesInCol > estimatedCountOfLines/2:
        estimatedCountOfLines=-1
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

