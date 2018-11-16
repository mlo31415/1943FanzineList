def Numeric(val):
    if val is int or val is float:
        return val
    try:
        return int(val)
    except:
        try:
            return float(val)
        except:
            return None


class FanzineIssueSpec:

    def __init__(self, Vol=None, Num=None, Whole=None, Year=None, Month=None):
        self._Vol=Vol
        self._Num=Num
        self._Whole=Whole
        self._Year=Year
        self._Month=Month
        self._UninterpretableText=None   # Ok, I give up.  Just hold the text as text.
        self._TrailingGarbage=None       # The uninterpretable stuff following the interpretable spec held in this instance

    def __eq__(self, other):
        if other is None:
            return False
        if self._Year != other._Year:
            return False
        if self._Month != other._Month:
            return False

        # Now it gets a bit complicated.  We need either Vol/Num or Whole to match. The other must also match or be None on at least one side
        # So, ("-" is None) the following match:
        # V1 N2 W3 matches V1 N2 W3
        # V1 N2 W3 matches V1 N2 W-
        # V1 N2 W3 matches V- N- W3
        # The following don't match:
        # V1 N2 W3 does not match V1 N2 W4
        # V1 N2 W3 matches V2 N2 W3
        vnMatches=False
        vnIsNone=False
        if self._Vol is None and other._Vol is None and self._Num is None and other._Num is None:
            vnIsNone=True
        if self._Vol == other._Vol and self._Num == other._Num:
            vnMatches=True

        vnOneIsNone=False
        if self._Vol is None and other._Vol is not None and self._Num is None and other._Num is not None:
            vnOneIsNone=True
        if self._Vol is not None and other._Vol is None and self._Num is not None and other._Num is None:
            vnOneIsNone=True

        wIsNone=False
        if self._Whole is None and other._Whole is None:
            wIsNone=True
        wMatches=False
        if self._Whole == other._Whole:
            wMatches=True
        wOneIsNone=False
        if (self._Whole is None and other._Whole is not None) or (self._Whole is not None and other._Whole is None):
            wOneIsNone=True

        if vnMatches and (wMatches or wOneIsNone or wIsNone):
            return True
        if wMatches and (vnMatches or vnOneIsNone or vnIsNone):
            return True

        return False

    def __ne__(self, other):
        return not self == other

    def Copy(self, other):
        self._Vol=other.Vol
        self._Num=other.Num
        self._Whole=other.Whole
        self._Year=other.Year
        self._Month=other.Month
        self._UninterpretableText=other.UninterpretableText
        self._TrailingGarbage=other.TrailingGarbage

    # .....................
    @property
    def Vol(self):
        return self._Vol

    @Vol.setter
    def Vol(self, val):
        self._Vol=Numeric(val)

    @Vol.getter
    def Vol(self):
        return self._Vol

    # .....................
    @property
    def Num(self):
        return self._Num

    @Num.setter
    def Num(self, val):
        self._Num=Numeric(val)

    @Num.getter
    def Num(self):
        return self._Num

    #.....................
    @property
    def Whole(self):
        return self._Whole

    @Whole.setter
    def Whole(self, val):
        self._Whole=Numeric(val)

    @Whole.getter
    def Whole(self):
        return self._Whole

    #.....................
    @property
    def Year(self):
        return self._Year

    @Year.setter
    def Year(self, val):
        self._Year=Numeric(val)

    @Year.getter
    def Year(self):
        return self._Year

    #.....................
    @property
    def Month(self):
        return self._Month

    @Month.setter
    def Month(self, val):
        self._Month=Numeric(val)

    @Month.getter
    def Month(self):
        return self._Month

    #.....................
    @property
    def UninterpretableText(self):
        return self._UninterpretableText

    @UninterpretableText.setter
    def UninterpretableText(self, val):
        if val is None:
            self._UninterpretableText=None
            return
        val=val.strip()
        if len(val) == 0:
            self._UninterpretableText=None
            return
        self._UninterpretableText=val

    @UninterpretableText.getter
    def UninterpretableText(self):
        return self._UninterpretableText

    #.....................
    @property
    def TrailingGarbage(self):
        return self._TrailingGarbage

    @TrailingGarbage.setter
    def TrailingGarbage(self, val):
        if val is None:
            self._TrailingGarbage=None
            return
        val=val.strip()
        if len(val) == 0:
            self._TrailingGarbage=None
            return
        self._TrailingGarbage=val

    @TrailingGarbage.getter
    def TrailingGarbage(self):
        return self._TrailingGarbage


    # .....................
    def SetDate(self, y, m):
        self.Year=Numeric(y)
        self.Month=Numeric(m)
        return self

    #.......................
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
            s=s+", TG='"+self.TrailingGarbage+"'"
        if self.UninterpretableText is not None:
            s=s+", UT='"+self.UninterpretableText+"'"
        s=s+")"

        return s

    #.......................
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
    def __init__(self, List=None):
        self._list=None
        self.List=List

    def AppendIS(self, fanzineIssueSpec):
        if isinstance(fanzineIssueSpec, FanzineIssueSpec):
            self._list.append(fanzineIssueSpec)
        elif isinstance(fanzineIssueSpec, IssueSpecList):
            self._list.extend(fanzineIssueSpec.List)
        else:
            print("****IssueSpecList.AppendIS() had strange input")
        return self

    def Extend(self, isl):
        self._list.extend(isl)
        return self

    def Str(self):      # Print out the ISL for debugging
        s=""
        for i in self._list:
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
        for i in self._list:
            if i is not None:
                if len(s) > 0:
                    s=s+", "
                s=s+i.Format()
        return s

    def __len__(self):
        return len(self._list)

    @property
    def List(self):
        return self._list

    @List.setter
    def List(self, val):
        if val is None:
            self._list=[]
            return self
        if isinstance(val, FanzineIssueSpec):
            self._list=[val]
            return self
        if isinstance(val, IssueSpecList):
            self._list=val.List
        print("****IssueSpecList.setter() had strange input")
        return self

    @List.getter
    def List(self):
        return self._list

    def __getitem__(self, key):
        return self._list[key]

    def __setitem__(self, key, value):
        self._list[key]=value
        return self