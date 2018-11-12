class FanzineIssueData:

    def __init__(self):
        self.DisplayName=None   # Includes issue number/date/whatever
        self.URL=None
        self.IssueSpec=None
        self._SeriesName=None

    def Format(self):
        if self.IssueSpec is not None:
            return self.SeriesName+" "+self.IssueSpec.Format()+": "+self.URL
        return self.SeriesName+": "+self.URL

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

