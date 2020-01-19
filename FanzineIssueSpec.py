# Try to make the input numeric
# Note that if it fails, it returns what came in.
def Numeric(val):
    if val == None:
        return None

    if isinstance(val, int) or isinstance(val, float):
        return val

    try:
        return int(val)
    except:
        try:
            return float(val)
        except:
            return val


class FanzineIssueSpec:

    def __init__(self, Vol=None, Num=None, NumSuffix=None, Whole=None, WSuffix=None, Year=None, Month=None):
        self._Vol=Vol
        self._Num=Num
        self._NumSuffix=NumSuffix  # For things like issue '17a'
        self._Whole=Whole
        self._WSuffix=WSuffix
        self._Year=Year
        self._Month=Month
        self._UninterpretableText=None   # Ok, I give up.  Just hold the text as text.
        self._TrailingGarbage=None       # The uninterpretable stuff following the interpretable spec held in this instance

    # Are the Num fields equal?
    # Both could be None; otherwise both must be equal
    def __NumEq__(self, other):
        return self._Num == other._Num and self._NumSuffix == other._NumSuffix

    def __VolEq__(self, other):
        return self._Vol == other._Vol

    def __WEq__(self, other):
        return self._Whole == other._Whole and self._WSuffix == other._WSuffix

    def __VNEq__(self, other):
        return self.__VolEq__(other) and self.__NumEq__(other)

    # Two issue designations are deemed to be equal if they are identical or if the VN matches while at least on of the Wholes in None or
    # is the Whole matches and at least one of the Vs and Ns is None.  (We would allow match of (W13, V3, N2) with (W13), etc.)
    def __IssueEQ__(self, other):
        if self.__VNEq__(other) and self.__WEq__(other):
            return True
        if (self._Whole is None or other._Whole is None) and self.__VNEq__(self):
            return True
        if (self._Num is None or self._Vol is None or other._Num is None or other._Vol is None) and self.__WEq__(other):
            return True
        return False

    def __eq__(self, other):
        if other is None:
            return False

        if not self.__IssueEQ__(other):
            return False

        # Now check for dates
        if self._Year == other._Year and self._Month == other._Month:
            return True
        return False

    def __ne__(self, other):
        return not self == other

    def Copy(self, other):
        self._Vol=other.Vol
        self._Num=other.Num
        self._NumSuffix=other.NumSuffix
        self._Whole=other.Whole
        self._WSuffix=other.WSuffix
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

    # .....................
    @property
    def NumSuffix(self):
        return self._NumSuffix

    @NumSuffix.setter
    def NumSuffix(self, val):
        self._NumSuffix=val

    @NumSuffix.getter
    def NumSuffix(self):
        return self._NumSuffix

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

    # .....................
    @property
    def WSuffix(self):
        return self._WSuffix

    @WSuffix.setter
    def WSuffix(self, val):
        self._WSuffix=val

    @WSuffix.getter
    def WSuffix(self):
        return self._WSuffix

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
    def SetWhole(self, t1, t2):
        self.Whole=t1
        if t2 is None:
            return self
        if len(t2) == 1 and t2.isalpha():  # E.g., 7a
            self.WSuffix=t2
        elif len(t2) == 2 and t2[0] == '.' and t2[1].isnumeric():  # E.g., 7.1
            self.WSuffix=t2
        else:
            self.TrailingGarbage=t2
        return self

    # .....................
    def SetDate(self, y, m):
        self.Year=Numeric(y)
        self.Month=Numeric(m)
        return self

    #.......................
    # Convert the IS into a debugging form
    def Str(self):
        if self.UninterpretableText is not None:
            return "IS("+self.UninterpretableText+")"

        v="-"
        if self.Vol is not None:
            v=str(self.Vol)
        n="-"
        if self.Num is not None:
            n=str(self.Num)
            if self.NumSuffix is not None:
                n=n+str(self.NumSuffix)
        w="-"
        if self.Whole is not None:
            w=str(self.Whole)
            if self.WSuffix is not None:
                n=n+str(self.WSuffix)
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
            tg=" "+self.TrailingGarbage

        if self.Vol is not None and self.Num is not None and self.Whole is not None:
            s="V"+str(self.Vol)+"#"+str(self.Num)
            if self.NumSuffix is not None:
                s+=str(self.NumSuffix)
            s+=" (#"+str(self.Whole)
            if self.WSuffix is not None:
                s+=str(self.WSuffix)
            s+=")"
            return s+tg

        if self.Vol is not None and self.Num is not None:
            s="V"+str(self.Vol)+"#"+str(self.Num)
            if self.NumSuffix is not None:
                s+=str(self.NumSuffix)
            return s+tg

        if self.Whole is not None:
            s="#"+str(self.Whole)
            if self.WSuffix is not None:
                s+=str(self.WSuffix)
            return s+tg

        if self.Year is not None:
            if self.Month is None:
                return str(self.Year)+tg
            else:
                return str(self.Year)+":"+str(self.Month)+tg


        return tg


#================================================================================
class IssueSpecList:
    def __init__(self, List=None):
        self.List=List

    def AppendIS(self, fanzineIssueSpec):
        if isinstance(fanzineIssueSpec, FanzineIssueSpec):
            self._list.append(fanzineIssueSpec)
        elif isinstance(fanzineIssueSpec, IssueSpecList):
            self._list.extend(fanzineIssueSpec.List)
        elif fanzineIssueSpec is None:
            return
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
        print("****IssueSpecList.List setter() had strange input")
        return self

    @List.getter
    def List(self):
        return self._list

    def __getitem__(self, key):
        return self._list[key]

    def __setitem__(self, key, value):
        self._list[key]=value
        return self
