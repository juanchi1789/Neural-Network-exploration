"""Convert the saved final-summary Markdown into one Overleaf-ready .tex file."""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Resumen de Trabajo Final.md"
TARGET = ROOT / "Resumen de Trabajo Final.tex"


PREAMBLE = r"""% ============================================================
% Resumen de Trabajo Final
% Archivo autónomo para Overleaf. Compilador: pdfLaTeX.
% Copiar todo este contenido dentro de main.tex.
% ============================================================
\documentclass[11pt,a4paper]{article}

% Idioma, codificación y tipografía
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-nodecimaldot]{babel}
\usepackage{lmodern}
\usepackage{microtype}
\DeclareUnicodeCharacter{2192}{\ensuremath{\rightarrow}}
\DeclareUnicodeCharacter{2193}{\ensuremath{\downarrow}}

% Página y estructura
\usepackage[a4paper,margin=2.4cm,headheight=15pt]{geometry}
\usepackage{parskip}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{fancyhdr}

% Matemática
\usepackage{amsmath,amssymb}

% Colores, enlaces y bloques de código
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{xurl}
\usepackage{listings}

% Paleta visual
\definecolor{ink}{HTML}{17263A}
\definecolor{muted}{HTML}{52657A}
\definecolor{accent}{HTML}{167D9A}
\definecolor{soft}{HTML}{F1F6F8}
\definecolor{line}{HTML}{CBD6DF}

% Enlaces y metadatos
\hypersetup{
  colorlinks=true,
  linkcolor=accent,
  urlcolor=accent,
  citecolor=accent,
  pdftitle={Resumen de Trabajo Final},
  pdfsubject={Simulación progresiva de un circuito neuromotor},
  pdfauthor={Neural Network Exploration}
}
\urlstyle{same}

% Encabezados
\titleformat{\section}
  {\Large\bfseries\color{ink}}{}{0pt}{}[\vspace{1mm}\color{line}\titlerule]
\titleformat{\subsection}
  {\large\bfseries\color{accent}}{}{0pt}{}
\titlespacing*{\section}{0pt}{1.1em}{0.55em}
\titlespacing*{\subsection}{0pt}{0.9em}{0.35em}
\setcounter{secnumdepth}{0}
\setcounter{tocdepth}{2}

% Listas
\setlist[itemize]{leftmargin=1.6em,itemsep=0.25em,topsep=0.35em}
\setlist[enumerate]{leftmargin=1.8em,itemsep=0.35em,topsep=0.35em}

% Código y diagramas de texto. Las reglas literate permiten compilar
% directamente las flechas presentes en el Markdown con pdfLaTeX.
\lstdefinestyle{reportcode}{
  basicstyle=\ttfamily\small,
  backgroundcolor=\color{soft},
  frame=single,
  rulecolor=\color{line},
  framesep=6pt,
  xleftmargin=0.5em,
  xrightmargin=0.5em,
  breaklines=true,
  columns=fullflexible,
  keepspaces=true,
  showstringspaces=false,
  literate={↓}{{$\downarrow$}}1 {→}{{$\rightarrow$}}1
}
\lstset{style=reportcode}

% Compatibilidad con listas compactas producidas por Pandoc
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

% Encabezado y pie
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\color{muted}Resumen de Trabajo Final}
\fancyhead[R]{\small\color{muted}Circuito neuromotor}
\fancyfoot[C]{\small\color{muted}\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\headrule}{\hbox to\headwidth{\color{line}\leaders\hrule height \headrulewidth\hfill}}

% Evita líneas desbordadas por URLs o nombres técnicos largos
\setlength{\emergencystretch}{3em}

\begin{document}

\begin{titlepage}
  \centering
  \vspace*{3.0cm}
  {\Huge\bfseries\color{ink} __TITLE__ \par}
  \vspace{1.2cm}
  {\LARGE\bfseries\color{accent} __SUBTITLE__ \par}
  \vfill
  {\large Neural Network Exploration \par}
  \vspace{0.3cm}
  {\large \today \par}
\end{titlepage}

\tableofcontents
\newpage

"""


ENDING = r"""

\end{document}
"""


def latex_escape_title(text):
    """Escape metadata text inserted directly into the LaTeX title page."""
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    }
    return "".join(replacements.get(character, character) for character in text)


def extract_title_and_body(markdown):
    """Use the first H1/H2 as cover metadata and keep the remaining content."""
    lines = markdown.splitlines()
    title = "Resumen de Trabajo Final"
    subtitle = "Simulación progresiva de un circuito neuromotor mediante neuronas de Izhikevich"
    remaining = []
    title_found = subtitle_found = False
    for line in lines:
        if not title_found and re.match(r"^#\s+", line):
            title = re.sub(r"^#\s+", "", line).strip()
            title_found = True
            continue
        if title_found and not subtitle_found and re.match(r"^##\s+", line):
            subtitle = re.sub(r"^##\s+", "", line).strip()
            subtitle_found = True
            continue
        remaining.append(line)
    return title, subtitle, "\n".join(remaining).strip() + "\n"


def pandoc_fragment(markdown_body):
    """Let Pandoc convert the Markdown body while keeping our custom preamble."""
    with tempfile.TemporaryDirectory(prefix="overleaf_tex_") as directory:
        source = Path(directory) / "body.md"
        target = Path(directory) / "body.tex"
        source.write_text(markdown_body, encoding="utf-8")
        subprocess.run(
            [
                "pandoc", str(source),
                "--from=markdown+tex_math_single_backslash+tex_math_dollars",
                "--to=latex",
                "--shift-heading-level-by=-1",
                f"--output={target}",
            ],
            check=True,
        )
        fragment = target.read_text(encoding="utf-8")
    # Listings supports line wrapping and maps the Unicode arrows for pdfLaTeX.
    return fragment.replace(r"\begin{verbatim}", r"\begin{lstlisting}").replace(
        r"\end{verbatim}", r"\end{lstlisting}"
    )


def build(source=SOURCE, target=TARGET):
    markdown = source.read_text(encoding="utf-8")
    title, subtitle, body = extract_title_and_body(markdown)
    preamble = PREAMBLE.replace("__TITLE__", latex_escape_title(title)).replace(
        "__SUBTITLE__", latex_escape_title(subtitle)
    )
    latex = preamble + pandoc_fragment(body) + ENDING
    target.write_text(latex, encoding="utf-8")
    return target


if __name__ == "__main__":
    print(build())
