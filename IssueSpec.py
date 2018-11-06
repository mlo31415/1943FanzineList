class IssueSpec:

    def __init__(self):
        self.Vol=None
        self.Num=None
        self.Whole=None
        self.Year=None
        self.Month=None
        self.UninterpretableText=None   # Ok, I give up.  Just hold the text as text.
        self.TrailingGarbage=None       # The uninterpretable stuff following the interpretable spec held in this instance

    def SetVN(self, v, n):
        self.Vol=v
        self.Num=n
        return self

    def SetW(self, w):
        self.Whole=w
        return self

    def SetDate(self, y, m):
        self.Year=y
        self.Month=m
        return self

    def SetUninterpretableText(self, str):
        self.UninterpretableText=str
        return self

    def SetTrailingGarbage(self, str):
        self.TrailingGarbage=str
        return self

    def Str(self):  # Convert the IS into a debugging form
        if self.UninterpretableText is not None:
            return "IS("+self.UninterpretableText+")"

        v="-"
        if self.Vol is not None:
            v=str(self.Vol)
        n="-"
        if self.Num is not None:
            n=str(self.Num)
        w="-"
        if self.Whole is not None:
            w=str(self.Whole)

        d=""
        if self.Year is not None:
            d=str(self.Year)
        if self.Month is not None:
            d=d+":"+str(self.Month)
        if d == "":
            d="-"

        s="IS(V"+v+", N"+n+", W"+w+", D"+d
        if self.TrailingGarbage != None:
            s=s+", G='"+self.TrailingGarbage+"'"
        return s+")"

    def Format(self):   # Convert the IS into a pretty string
        if self.UninterpretableText is not None:
            return self.UninterpretableText

        tg=""
        if self.TrailingGarbage is not None:
            tg=self.TrailingGarbage

        if self.Vol is not None and self.Num is not None:
            return "V"+str(self.Vol)+"#"+str(self.Num)+tg

        if self.Whole is not None:
            return "#"+str(self.Whole)+tg

        if self.Year is not None:
            if self.Month is None:
                return str(self.Year)+tg
            else:
                return str(self.Year)+":"+str(self.Month)+tg

        return tg


#================================================================================
class IssueSpecList:
    def __init__(self):
        self.list=[]

    def AppendIS(self, issuespec):
        self.list.append(issuespec)
        return self

    def AppendVIS(self, vol, issuelist):
        for i in issuelist:
            self.Append(IssueSpec().SetVN(vol, i))
        return self

    def Extend(self, isl):
        self.list.extend(isl)
        return self

    def Str(self):      # Print out the ISL for debugging
        s=""
        for i in self.list:
            if len(s) > 0:
                s=s+",  "
            if i != None:
                s=s+i.Str()
            else:
                s=s+"Missing ISlist"
        if len(s) == 0:
            s="Empty ISlist"
        return s

    def Format(self):   # Format the ISL for pretty
        s=""
        for i in self.list:
            if i is not None:
                if len(s) > 0:
                    s=s+", "
                s=s+i.Format()
        return s

    def len(self):
        return len(self.list)

    def List(self):
        return self.list

    def __getitem__(self, key):
        return self.list[key]

    def __setitem__(self, key, value):
        self.list[key]=value
        return self