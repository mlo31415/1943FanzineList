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

    def SetDate(selfself, y, m):
        self=Year=y
        self.Month=m
        return self

    def SetUninterpretableText(self, str):
        self.UninterpretableText=str
        return self

    def SetTrailingGarbage(self, str):
        self.TrailingGarbage=str
        return self

    def Str(self):
        if self.UninterpretableText != None:
            return "IS("+self.UninterpretableText+")"

        v="-"
        if self.Vol != None:
            v=str(self.Vol)
        n="-"
        if self.Num != None:
            n=str(self.Num)
        w="-"
        if self.Whole != None:
            w=str(self.Whole)

        d="-"
        if self.Year != None:
            d=str(self.Year)
        if self.Month != None:
            d=":"+str(self.Month)

        s="IS(V"+v+", N"+n+", W"+w+", D"+d
        if self.TrailingGarbage != None:
            s=s+", G='"+self.TrailingGarbage+"'"
        return s+")"


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

    def Str(self):
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

    def len(self):
        return len(self.list)

    def List(self):
        return self.list