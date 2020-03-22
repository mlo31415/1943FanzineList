from typing import TextIO, List, Tuple, Optional, Callable
from FanzineIssueSpecPackage import FanzineIssueSpec

# class FanzineIssueData holds information about a specific issue of a fanzine.
#   Its display name (the name used to display this particular issue), e.g., File770 #34
#   Its URL (on fanac.org or elsewhere)
#   Its FanzineIssueSpec (e.g., WholeNum=34)
#   Its series name (the name of the fanzine series to which it belongs), e.g., File770.

class FanzineIssueData:

    def __init__(self, DisplayName: Optional[str]=None, URL: Optional[str]=None, FanzineIssueSpec: Optional[FanzineIssueSpec]=None, SeriesName: Optional[str]=None, Fanac: bool=False) -> None:
        self.DisplayName=DisplayName   # Includes issue number/date/whatever
        self.URL=URL
        self.FanzineIssueSpec=FanzineIssueSpec
        self._SeriesName=SeriesName
        self.Fanac=Fanac

    # .....................
    def __str__(self) -> str:   #TODO: Note that this will wrongly name those issues with special, variant names
        out=""
        if self.SeriesName is not None:
            out=self.SeriesName
        if self.FanzineIssueSpec is not None and not self.FanzineIssueSpec.IsEmpty():
            out=out+" "+str(self.FanzineIssueSpec)
        if self.URL is not None:
            out=out+" "+self.URL
        return out.strip()

    # .....................
    @property
    def SeriesName(self) -> str:
        return self._SeriesName

    @SeriesName.setter
    def SeriesName(self, val: Optional[str]) -> None:
        if val is not None:
            val=val.strip()
        self._SeriesName=val
