from typing import AnyStr
from gentopia.tools.basetool import *
import urllib.request
import PyPDF2
import io


class PdfReaderArgs(BaseModel):
    query: str = Field(..., description="a url to the pdf")


class PdfReader(BaseTool):
    """Tool that adds the capability to read a pdf file."""

    name = "pdf_reader"
    description = ("A tool to read a pdf file."
                    "Expects a pdf url.")

    args_schema: Optional[Type[BaseModel]] = PdfReaderArgs

    def _run(self, query: AnyStr) -> str:
        request = urllib.request.Request(query, headers={'User-Agent': "Magic Browser"})
        file = urllib.request.urlopen(request).read()
        file_bytes = io.BytesIO(file)
        pdf = PyPDF2.PdfReader(file_bytes)
        doc = "\n\n".join(pdf.pages[i].extract_text() for i in range(len(pdf.pages)))
        return doc

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


if __name__ == "__main__":
    ans = PdfReader()._run("https://arxiv.org/pdf/2308.04030.pdf")
    print(ans)