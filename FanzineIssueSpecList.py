import FanzineIssueSpec

#================================================================================
# A Fanzine issue spec list contains the information to handle a list of issues of a single fanzine.
# It includes the series name, editors(s), and a list of Fanzine Issue specs.
#TODO: This can be profitable extended by changing the ISS class to include specific names and editors for each issue, since sometimes
#TODO: a series does not have a consistant set throughout.

class FanzineIssueSpecList:
    def __init__(self, List=None):
        self.List=List

    def AppendIS(self, fanzineIssueSpec):
        if isinstance(fanzineIssueSpec, FanzineIssueSpec.FanzineIssueSpec):
            self._list.append(fanzineIssueSpec)
        elif isinstance(fanzineIssueSpec, FanzineIssueSpecList):
            self._list.extend(fanzineIssueSpec.List)
        elif fanzineIssueSpec is None:
            return
        else:
            print("****IssueSpecList.AppendIS() had strange input")
        return self

    def Extend(self, isl):
        self._list.extend(isl)
        return self

    def Str(self):      # Print out the ISL for debugging
        s=""
        for i in self._list:
            if len(s) > 0:
                s=s+",  "
            if i is not None:
                s=s+i.Str()
            else:
                s=s+"Missing ISlist"
        if len(s) == 0:
            s="Empty ISlist"
        return s

    def Format(self):   # Format the ISL for pretty
        s=""
        for i in self._list:
            if i is not None:
                if len(s) > 0:
                    s=s+", "
                s=s+i.Format()
        return s

    def __len__(self):
        return len(self._list)

    @property
    def List(self):
        return self._list

    @List.setter
    def List(self, val):
        if val is None:
            self._list=[]
            return self
        if isinstance(val, FanzineIssueSpec.FanzineIssueSpec):
            self._list=[val]
            return self
        if isinstance(val, FanzineIssueSpecList):
            self._list=val.List
        print("****IssueSpecList.List setter() had strange input")
        return self

    @List.getter
    def List(self):
        return self._list

    def __getitem__(self, key):
        return self._list[key]

    def __setitem__(self, key, value):
        self._list[key]=value
        return self
