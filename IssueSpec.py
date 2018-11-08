def Int(val):
    if val is int:
        return val
    try:
        return int(val)
    except:
        return None


class IssueSpec:

    def __init__(self, Vol=None, Num=None, Whole=None, Year=None, Month=None):
        self._Vol=Vol
        self._Num=Num
        self._Whole=Whole
        self.Year=Year
        self.Month=Month
        self.UninterpretableText=None   # Ok, I give up.  Just hold the text as text.
        self.TrailingGarbage=None       # The uninterpretable stuff following the interpretable spec held in this instance

    # .....................
    @property
    def Vol(self):
        return self._Vol

    @Vol.setter
    def Vol(self, val):
        self._Vol=Int(val)

    @Vol.getter
    def Vol(self):
        return self._Vol

    # .....................
    @property
    def Num(self):
        return self._Num

    @Num.setter
    def Num(self, val):
        self._Num=Int(val)

    @Num.getter
    def Num(self):
        return self._Num

    #.....................
    @property
    def Whole(self):
        return self._Whole

    @Whole.setter
    def Whole(self, val):
        self._Whole=Int(val)

    @Whole.getter
    def Whole(self):
        return self._Whole

    # .....................
    def SetDate(self, y, m):
        self.Year=Int(y)
        self.Month=Int(m)
        return self

    def SetUninterpretableText(self, s):
        if s is not None and len(s) > 0:
            self.UninterpretableText=s
        return s

    def SetTrailingGarbage(self, s):
        if s is not None and len(s) > 0:
            self.TrailingGarbage=s
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
        if self.TrailingGarbage is not None:
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
            self.list.append(IssueSpec(Vol=vol, Num=i))
        return self

    def Extend(self, isl):
        self.list.extend(isl)
        return self

    def Str(self):      # Print out the ISL for debugging
        s=""
        for i in self.list:
            if len(s) > 0:
                s=s+",  "
            if i is not None:
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

    def __len__(self):
        return len(self.list)

    def List(self):
        return self.list

    def __getitem__(self, key):
        return self.list[key]

    def __setitem__(self, key, value):
        self.list[key]=value
        return self