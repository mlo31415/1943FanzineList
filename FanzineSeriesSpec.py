

class FanzineSeriesSpec:

    def __init__(self):
        self.IssueSpecList=None
        self._Name=None
        self.Editor=None
        self.Eligible=None
        self.Notes=None

        # .....................
        @property
        def Name(self):
            return self._Name

        @Name.setter
        def Vol(self, val):
            if val is not None:
                val=val.strip()
            self._Name=val

        @Name.getter
        def Name(self):
            return self._Name

    def Str(self):  # Convert the FSS into a debugging form
        isl="-"
        if self.IssueSpecList is not None:
            isl=self.IssueSpecList.Format()

        na="-"
        if self._Name is not None:
            na=self._Name

        e="-"
        if self.Editor is not None:
            e=self.Editor

        no="-"
        if self.Notes is not None:
            no=self.Notes

        return "FSS(N"+na+", Ed"+e+", No"+no+", ISL("+isl+"), E"+e+")"


    def Format(self):  # Pretty print the FSS

        out=""
        if self.Name is not None:
            out=self.Name

        if self.Editor is not None and len(self.Editor) > 0:
            out=out+"   ("+self.Editor+")"

        if self.Notes is not None and len(self.Notes) > 0:
            for n in self.Notes:
                out=out+"   {"+n+"}"

        if self.IssueSpecList is not None and len(self.IssueSpecList) > 0:
            out=out+"  "+self.IssueSpecList.Format()

        if self.Eligible:
            out=out+"   Eligible!"
        return out
