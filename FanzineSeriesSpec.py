from typing import TextIO, List, Tuple, Optional, Callable
from FanzineIssueSpecPackage import FanzineIssueSpecList

# This is a class used to hold a list of many issues of a single fanzine.
class FanzineSeriesSpec:

    def __init__(self)  -> None:
        self._FISL: Optional[FanzineIssueSpecList]=None     # A list of FanzineIssueSpecs
        self._SeriesName: Optional[str]=None
        self._Editor: Optional[str]=None
        self._Eligible: Optional[bool]=None
        self._Notes: Optional[str]=None
        self._SeriesURL: Optional[str]=None

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
    def Editor(self) -> str:
        if self._Editor is None:
            return ""
        return self._Editor

    @Editor.setter
    def Editor(self, val: Optional[str]) -> None:
        self._Editor=val

    # .....................
    @property
    def Eligible(self) -> bool:
        if self._Eligible is None:
            return False
        return self._Eligible

    @Eligible.setter
    def Eligible(self, val: Optional[bool]) -> None:
        self._Eligible=val

    # .....................
    @property
    def FISL(self) -> Optional[FanzineIssueSpecList]:
        if self._FISL is None:
            return None
        return self._FISL

    @FISL.setter
    def FISL(self, val: Optional[FanzineIssueSpecList]) -> None:
        self._FISL=val

    # .....................
    @property
    def Notes(self) -> str:
        if self._Notes is None:
            return ""
        return self._Notes

    @Notes.setter
    def Notes(self, val: Optional[str]) -> None:
        self._Notes=val

    # .....................
    @property
    def SeriesURL(self) -> str:
        if self._SeriesURL is None:
            return ""
        return self._SeriesURL

    @SeriesURL.setter
    def SeriesURL(self, val: Optional[str]) -> None:
        self._SeriesURL=val

    # .....................
    def LenFISL(self) -> int:
        if self._FISL is None:
            return 0
        return len(self._FISL)

    # .....................
    def DebugStr(self) -> str:  # Convert the FSS into a debugging form
        isl="-"
        if self.LenFISL() > 0:
            isl=self._FISL.DebugStr()

        sn="-"
        if self._SeriesName is not None:
            sn=self._SeriesName

        ed="-"
        if self._Editor is not None:
            ed=self._Editor

        nt=""
        if self._Notes is not None:
            for note in self._Notes:
                if len(nt) > 0:
                    nt+=" "
                nt+=note
            if len(nt) == 0:
                nt="-"

        el="-"
        if self._Eligible is not None:
            el="T" if self._Eligible else "F"

        u="-"
        if self._SeriesURL is not None:
            u=self._SeriesURL

        return "FSS(SN:"+sn+", ISL:"+isl+", Ed:"+ed+", NT:"+nt+", El:"+el+" URL="+u+")"

    # .....................
    def __str__(self) -> str:  # Pretty print the FSS
        out=""
        if self.SeriesName is not None:
            out=self.SeriesName

        if self._Editor is not None and len(self._Editor) > 0:
            out=out+"   ("+self._Editor+")"

        if self._Notes is not None and len(self._Notes) > 0:
            for n in self._Notes:
                out=out+"   {"+n+"}"

        if self.LenFISL() > 0:
            out=out+"  "+str(self._FISL)

        if self._Eligible:
            out=out+"   Eligible!"
        return out
