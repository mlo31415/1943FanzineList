class IssueData:

    def __init__(self):
        self.DisplayName=None   # Includes issue number/date/whatever
        self.URL=None
        self.IssueSpec=None
        self._Name=None

    def Format(self):
        return self.Name+" "+self.IssueSpec.Format()+": "+self.URL

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

