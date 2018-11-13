class FanzineIssueData:

    def __init__(self):
        self.DisplayName=None   # Includes issue number/date/whatever
        self.URL=None
        self.IssueSpec=None
        self._SeriesName=None

    def Format(self):
        out=""
        if self.SeriesName is not None:
            out=self.SeriesName
        if self.IssueSpec is not None:
            out=out+" "+self.IssueSpec.Format()
        if self.URL is not None:
            out=out+" "+self.URL
        return out

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

