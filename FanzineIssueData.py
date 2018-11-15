class FanzineIssueData:

    def __init__(self, DisplayName=None, URL=None, FanzineIssueSpec=None, SeriesName=None):
        self.DisplayName=DisplayName   # Includes issue number/date/whatever
        self.URL=URL
        self.FanzineIssueSpec=FanzineIssueSpec
        self._SeriesName=SeriesName

    def Format(self):
        out=""
        if self.SeriesName is not None:
            out=self.SeriesName
        if self.FanzineIssueSpec is not None:
            out=out+" "+self.FanzineIssueSpec.Format()
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

