

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

        return "FSS(N"+na+", E"+e+", No"+no+", ISL("+isl+"), E"+e+")"

