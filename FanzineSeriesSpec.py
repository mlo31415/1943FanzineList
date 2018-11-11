

class FanzineSeriesSpec:

    def __init__(self):
        self.IssueSpecList=None
        self._SeriesName=None
        self.Editor=None
        self.Eligible=None
        self.Notes=None

    # .....................
    @property
    def SeriesName(self):
        return self._SeriesName

    @SeriesName.setter
    def SeriesName(self, val):
        if val is not None:
            val=val.strip()
        self._SeriesName=val

    @SeriesName.getter
    def SeriesName(self):
        return self._SeriesName

    def Str(self):  # Convert the FSS into a debugging form
        isl="-"
        if self.IssueSpecList is not None:
            isl=self.IssueSpecList.Format()

        na="-"
        if self._SeriesName is not None:
            na=self._SeriesName

        e="-"
        if self.Editor is not None:
            e=self.Editor

        no=""
        if self.Notes is not None:
            for note in self.Notes:
                if len(no) > 0:
                    no+=" "
                no+=note
            if len(no) == 0:
                no="-"

        return "FSS(N"+na+", Ed"+e+", No"+no+", ISL("+isl+"), E"+e+")"


    def Format(self):  # Pretty print the FSS
        out=""
        if self.SeriesName is not None:
            out=self.SeriesName

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
