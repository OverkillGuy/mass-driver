"""Google/Numpy-style-aware docstring parser for Myst

Sphinx-autodoc2, despite reading myst-markdown files, cannot parse Google docstrings.

Add support for the "Adds/Returns/Raises" docstring flags, by parsing them via Napoleon
plugin. Using code from:

https://github.com/sphinx-extensions2/sphinx-autodoc2/issues/33#issuecomment-2564137728
"""


from docutils import nodes
from myst_parser.parsers.sphinx_ import MystParser
from sphinx.ext.napoleon import docstring


class NapoleonParser(MystParser):
    def parse(self, input_string: str, document: nodes.document) -> None:
        parsed_content = "```{eval-rst}\n"
        parsed_content += str(
            docstring.GoogleDocstring(str(docstring.NumpyDocstring(input_string)))
        )
        parsed_content += "\n```\n"
        return super().parse(parsed_content, document)

Parser = NapoleonParser
