from typing import TextIO, List, Tuple, Optional, Callable
from FanzineIssueSpecPackage import FanzineIssueSpec

# class FanzineIssueData holds information about a specific issue of a fanzine.
#   Its display name (the name used to display this particular issue), e.g., File770 #34
#   Its URL (on fanac.org or elsewhere)
#   Its FanzineIssueSpec (e.g., WholeNum=34)
#   Its series name (the name of the fanzine series to which it belongs), e.g., File770.

class FanzineIssueData:

    def __init__(self, DisplayName: Optional[str]=None, URL: Optional[str]=None, FIS: Optional[FanzineIssueSpec]=None, SeriesName: Optional[str]=None) -> None:
        self._DisplayName=DisplayName   # Includes issue number/date/whatever
        # TODO: Need to resolve displayname and seriesname. Does DisplayName include issue #?  Should that come from FIS or override it?
        self.URL=URL                    # URL of issue
        self.FIS=FIS                    # FIS of issue
        self._SeriesName=SeriesName     # Name of fanzine sof hwich this is an issue


    # .....................
    def __str__(self) -> str:   #TODO: Note that this will wrongly name those issues with special, variant names
        out=""
        if self.SeriesName is not None:
            out=self.SeriesName
        if self.FIS is not None and not self.FIS.IsEmpty():
            out=out+" "+str(self.FIS)
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

    # .....................
    @property
    def DisplayName(self) -> str:
        if self._DisplayName is not None:
            return self._DisplayName
        if self.FIS is not None:
            return self._SeriesName+" "+str(self.FIS)
        return self._SeriesName

    @DisplayName.setter
    def DisplayName(self, val: Optional[str]) -> None:
        if val is not None:
            val=val.strip()
        self._DisplayName=val


    # .....................
    @property
    def DirURL(self) -> Optional[str]:
        return self._DirURL

    @DirURL.setter
    def DirURL(self, val: Optional[str]) -> None:
        self._DirURL=val