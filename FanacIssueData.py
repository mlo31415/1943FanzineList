class FanacIssueData:

    def __init__(self):
        self.DisplayName=None
        self.DirURL=None
        self.Filename=None
        self.IssueSpec=None
        self._Name=None

    def Format(self):
        return self.Name+" "+self.IssueSpec.Format()+": "+self.DirURL+"/"+self.DisplayName

    # .....................
    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, val):
        if val is not None:
            val=val.strip()
        self._Name=val

    @Name.getter
    def Name(self):
        return self._Name

