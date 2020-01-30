# A FanzineIssueSpec contains the information for one fanzine issue specification, e.g.:
#  V1#2, #3, #2a, Dec 1967, etc.
# It can be a volume+number or a whole numer or a date. (It can be more than one of these, also, and all are retained.)

from Helpers import ToNumeric

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

    def CaseInsensitiveCompare(self, s1, s2):
        if s1 == s2:
            return True
        if s1 is None or s2 is None:
            return False    # We already know that s1 and s2 are different
        return s1.lower() == s2.lower()

    # Are the Num fields equal?
    # Both could be None; otherwise both must be equal
    def __NumEq__(self, other):
        return self._Num == other._Num and self.CaseInsensitiveCompare(self._NumSuffix, other._NumSuffix)

    def __VolEq__(self, other):
        return self._Vol == other._Vol

    def __WEq__(self, other):
        return self._Whole == other._Whole and self.CaseInsensitiveCompare(self._WSuffix, other._WSuffix)

    def __VNEq__(self, other):
        return self.__VolEq__(other) and self.__NumEq__(other)

    # Two issue designations are deemed to be equal if they are identical or if the VN matches while at least on of the Wholes in None or
    # is the Whole matches and at least one of the Vs and Ns is None.  (We would allow match of (W13, V3, N2) with (W13), etc.)
    def __IssueEQ__(self, other):
        if self.__VNEq__(other) and self.__WEq__(other):
            return True
        if (self._Whole is None or other._Whole is None) and self.__VNEq__(other):
            return True
        if (self._Num is None or self._Vol is None or other._Num is None or other._Vol is None) and self.__WEq__(other):
            return True
        return False

    def __eq__(self, other):
        if other is None:
            return False

        if self.__IssueEQ__(other):
            return True

        # Now check for dates
        if self._Year is not None and self._Year == other._Year and self._Month is not None and self._Month == other._Month:
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
        self._Vol=ToNumeric(val)

    @Vol.getter
    def Vol(self):
        return self._Vol

    # .....................
    @property
    def Num(self):
        return self._Num

    @Num.setter
    def Num(self, val):
        self._Num=ToNumeric(val)

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
        self._Whole=ToNumeric(val)

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
        self._Year=ToNumeric(val)

    @Year.getter
    def Year(self):
        return self._Year

    #.....................
    @property
    def Month(self):
        return self._Month

    @Month.setter
    def Month(self, val):
        self._Month=ToNumeric(val)

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
        self.Year=ToNumeric(y)
        self.Month=ToNumeric(m)
        return self

    #.......................
    # Convert the IS into a debugging form
    def DebugStr(self):
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
    def IsEmpty(self):
        return self._Whole is None and self._Num is None and self._WSuffix is None and self._NumSuffix is None and self._Month is None and self._UninterpretableText and \
            self._TrailingGarbage is None and self._Vol is None and self._Year is None

    #.......................
    def __str__(self):   # Convert the IS into a pretty string
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
