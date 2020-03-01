from typing import TextIO, List, Tuple, Optional, Callable

class FanzineSeriesSpec:

    def __init__(self)  -> None:
        self.FanzineIssueSpecList=None     # A list of FanzineIssueSpecs
        self._SeriesName=None
        self.Editor=None
        self.Eligible=None
        self.Notes=None
        self.SeriesURL=None

    # .....................
    @property
    def SeriesName(self) -> str:
        return self._SeriesName

    @SeriesName.setter
    def SeriesName(self, val: Optional[str]) -> None:
        if val is not None:
            val=val.strip()
        self._SeriesName=val
    #
    # @SeriesName.getter
    # def SeriesName(self) -> str:
    #     return self._SeriesName

    def LenFIS(self) -> int:
        if self.FanzineIssueSpecList is None:
            return 0
        return len(self.FanzineIssueSpecList)

    def DebugStr(self) -> str:  # Convert the FSS into a debugging form
        isl="-"
        if self.LenFIS() > 0:
            isl=self.FanzineIssueSpecList.DebugStr()

        sn="-"
        if self._SeriesName is not None:
            sn=self._SeriesName

        ed="-"
        if self.Editor is not None:
            ed=self.Editor

        nt=""
        if self.Notes is not None:
            for note in self.Notes:
                if len(nt) > 0:
                    nt+=" "
                nt+=note
            if len(nt) == 0:
                nt="-"

        el="-"
        if self.Eligible is not None:
            el="T" if self.Eligible else "F"

        u="-"
        if self.SeriesURL is not None:
            u=self.SeriesURL

        return "FSS(SN:"+sn+", ISL:"+isl+", Ed:"+ed+", NT:"+nt+", El:"+el+" URL="+u+")"


    def __str__(self) -> str:  # Pretty print the FSS
        out=""
        if self.SeriesName is not None:
            out=self.SeriesName

        if self.Editor is not None and len(self.Editor) > 0:
            out=out+"   ("+self.Editor+")"

        if self.Notes is not None and len(self.Notes) > 0:
            for n in self.Notes:
                out=out+"   {"+n+"}"

        if self.LenFIS() > 0:
            out=out+"  "+str(self.FanzineIssueSpecList)

        if self.Eligible:
            out=out+"   Eligible!"
        return out
