import re as Regex

# Read the list of 1943 fanzines and parse them
# The format of a line is: <name> (<editor> & <editor>) >comma-separated list of issues> {comment 1} {comment 2}
# the name and editor are always present
with open("fanzines of 1943.txt") as f:
    lines=f.readlines()
    lines=[l.strip() for l in lines]   # Remove whitespace including trailing '\n'

for line in lines:
    m=Regex.search("(.*)\((.*)\)(.*){(.*)}$", line)     # First look for line with comments
    if m is not None:
        print("1: "+str(m.groups()))
    else:
        m=Regex.search("(.*)\((.*)\)(.*)$", line)  # Try it without comments
        if m is not None:
            print("2: "+str(m.groups()))
        else:
            print("No match: "+line)
    i=0

i=0

