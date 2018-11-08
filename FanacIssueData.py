class FanacIssueData:

    def __init__(self):
        self.DisplayName=None
        self.DirURL=None
        self.Filename=None
        self.IssueSpec=None
        self.Name=None

    def Format(self):
        return self.Name+" "+self.IssueSpec.Format()+": "+self.DirURL+"/"+self.DisplayName

