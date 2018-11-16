

class FanzineSeriesSpec:

    def __init__(self):
        self.IssueSpecList=None     # A FanzineIssueSpec
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

        sn="-"
        if self._SeriesName is not None:
            sn=self._SeriesName

        ed="-"
        if self.Editor is not None:
            ed=self.Editor

        nt=""
        if self.Notes is not None:
            for note in self.Notes:
                if len(nt) > 0:
                    nt+=" "
                nt+=note
            if len(nt) == 0:
                nt="-"

        el="-"
        if self.Eligible is not None:
            el="T" if self.Eligible else "F"

        return "FSS(SN:"+sn+", ISL:"+isl+", Ed:"+ed+", NT:"+nt+", El:"+el+")"


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
