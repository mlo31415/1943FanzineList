

class FanzineSeriesSpec:

    def __init__(self):
        self.IssueSpecList=None
        self.Name=None
        self.Editor=None
        self.Eligible=None
        self.Notes=None

    def Str(self):  # Convert the FSS into a debugging form
        isl="-"
        if self.IssueSpecList is not None:
            isl=self.IssueSpecList.Format()

        na="-"
        if self.Name is not None:
            na=self.Name

        e="-"
        if self.Editor is not None:
            e=self.Editor

        no="-"
        if self.Notes is not None:
            no=self.Notes

        return "FSS(N"+na+", Ed"+e+", No"+no+", ISL("+isl+"), E"+e+")"

    def Format(self):  # Pretty print the FSS
        isl=""
        if self.IssueSpecList is not None:
            isl=self.IssueSpecList.Format()

        na=""
        if self.Name is not None:
            na=self.Name

        e=""
        if self.Editor is not None:
            e=self.Editor

        no=""
        if self.Notes is not None:
            no=self.Notes

        out=na
        if len(e) > 0:
            out=out+"   ("+e+")"
        if len(no) > 0:
            out=out+"   {"+str(no)+"}"
        if len(isl) > 0:
            out=out+"  "+isl
        if self.Eligible:
            out=out+"   Eligible!"
        return out
