%% simplehipstercv.cls
%% A simplified class file for hipster CV layouts
%% Based on the hipstercv template

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{simplehipstercv}[2025/10/31 Simple Hipster CV Class]

% Base class
\LoadClass[11pt,a4paper]{article}

% Required packages
\RequirePackage{xcolor}
\RequirePackage{fontawesome5}
\RequirePackage{paracol}
\RequirePackage{tikz}
\RequirePackage{hyperref}
\RequirePackage{graphicx}
\RequirePackage{tabularx}
\RequirePackage{array}

% Class options for color themes
\DeclareOption{darkhipster}{%
  \definecolor{headercolour}{RGB}{0,0,0}
  \definecolor{cvgreen}{RGB}{150,200,150}
  \definecolor{cvpurple}{RGB}{180,150,200}
  \definecolor{cvred}{RGB}{200,100,100}
  \definecolor{headerblue}{RGB}{100,150,200}
  \definecolor{skilllabelcolour}{RGB}{80,80,80}
  \definecolor{iconcolour}{RGB}{255,255,255}
}

\DeclareOption{lighthipster}{%
  \definecolor{headercolour}{RGB}{90,90,90}
  \definecolor{cvgreen}{RGB}{100,180,100}
  \definecolor{cvpurple}{RGB}{150,120,180}
  \definecolor{cvred}{RGB}{180,80,80}
  \definecolor{headerblue}{RGB}{80,120,180}
  \definecolor{skilllabelcolour}{RGB}{120,120,120}
  \definecolor{iconcolour}{RGB}{255,255,255}
}

\DeclareOption{pastel}{%
  \definecolor{headercolour}{RGB}{120,120,120}
  \definecolor{cvgreen}{RGB}{150,200,180}
  \definecolor{cvpurple}{RGB}{180,170,200}
  \definecolor{cvred}{RGB}{200,150,150}
  \definecolor{headerblue}{RGB}{150,180,200}
  \definecolor{skilllabelcolour}{RGB}{140,140,140}
  \definecolor{iconcolour}{RGB}{255,255,255}
}

\DeclareOption{allblack}{%
  \definecolor{headercolour}{RGB}{0,0,0}
  \definecolor{cvgreen}{RGB}{0,0,0}
  \definecolor{cvpurple}{RGB}{0,0,0}
  \definecolor{cvred}{RGB}{0,0,0}
  \definecolor{headerblue}{RGB}{0,0,0}
  \definecolor{skilllabelcolour}{RGB}{0,0,0}
  \definecolor{iconcolour}{RGB}{255,255,255}
}

\DeclareOption{grey}{%
  \definecolor{headercolour}{RGB}{100,100,100}
  \definecolor{cvgreen}{RGB}{130,130,130}
  \definecolor{cvpurple}{RGB}{120,120,120}
  \definecolor{cvred}{RGB}{110,110,110}
  \definecolor{headerblue}{RGB}{120,120,120}
  \definecolor{skilllabelcolour}{RGB}{100,100,100}
  \definecolor{iconcolour}{RGB}{255,255,255}
}

\DeclareOption{verylight}{%
  \definecolor{headercolour}{RGB}{150,150,150}
  \definecolor{cvgreen}{RGB}{180,220,180}
  \definecolor{cvpurple}{RGB}{200,190,220}
  \definecolor{cvred}{RGB}{220,180,180}
  \definecolor{headerblue}{RGB}{180,200,220}
  \definecolor{skilllabelcolour}{RGB}{160,160,160}
  \definecolor{iconcolour}{RGB}{255,255,255}
}

\DeclareOption{withoutsidebar}{%
  % Single column layout
  \AtBeginDocument{\columnsep=0pt}
}

\ExecuteOptions{lighthipster} % default
\ProcessOptions\relax

% Hyperref setup
\hypersetup{
  colorlinks=true,
  linkcolor=cvgreen,
  urlcolor=cvgreen,
  pdfborderstyle={/S/U/W 1}
}

% Commands for CV layout

% Simple header command
\newcommand{\simpleheader}[5]{%
  % #1 = background color
  % #2 = first name
  % #3 = last name  
  % #4 = job title
  % #5 = text color
  \begin{tikzpicture}[remember picture, overlay]
    \node[rectangle, fill=#1, anchor=north, minimum width=\paperwidth, minimum height=3cm](header) at (current page.north){};
    \node[anchor=center](name) at (header) {%
      \fontsize{40pt}{60pt}\color{#5}%
      {\textbf{#2}}~{\textbf{#3}}%
    };
    \node[anchor=north](job) at (name.south) {%
      \fontsize{14pt}{24pt}\color{#5}%
      #4%
    };
  \end{tikzpicture}
  \vspace{2.5cm}
}

% Background box for section titles
\newcommand{\bg}[3]{%
  % #1 = background color
  % #2 = text color
  % #3 = text
  \colorbox{#1}{\textbf{\color{#2}#3}}%
}

% Icon bubble for contact info
\newcommand{\infobubble}[4]{%
  % #1 = icon
  % #2 = background color
  % #3 = text color
  % #4 = text
  \par\noindent
  \begin{tikzpicture}
    \node[circle, fill=#2, inner sep=2pt, text=#3](icon){#1};
    \node[anchor=west, text=#3] at (icon.east){\quad #4};
  \end{tikzpicture}
}

% Proficiency bar for skills
\newcommand{\barrule}[3]{%
  % #1 = proficiency (0.0-1.0)
  % #2 = height
  % #3 = color
  \begin{tikzpicture}
    \fill[color=#3] (0,0) rectangle (#1*5,#2);
    \draw[color=black!30] (0,0) rectangle (5,#2);
  \end{tikzpicture}%
}

% Picture fraction for language proficiency
\newcommand{\pictofraction}[6]{%
  % #1 = icon
  % #2 = filled color
  % #3 = number filled
  % #4 = empty color
  % #5 = number empty
  % #6 = size
  \foreach \n in {1,...,#3}{{\color{#2}#1}}%
  \foreach \n in {1,...,#5}{{\color{#4}#1}}%
}

% CV event entry
\newcommand{\cvevent}[6]{%
  % #1 = dates
  % #2 = title
  % #3 = subtitle
  % #4 = location
  % #5 = description
  % #6 = icon (optional)
  \textbf{#1} & \textbf{#2} \newline \textit{#3} \newline #4 \newline\newline #5 & \ifx&#6&\else\includegraphics[width=1cm]{#6}\fi
}

% CV degree entry
\newcommand{\cvdegree}[6]{%
  % #1 = year
  % #2 = degree
  % #3 = type
  % #4 = institution
  % #5 = description
  % #6 = icon (optional)
  \textbf{#1} & \textbf{#2} \newline \textit{#3} \newline #4 \newline #5 & \ifx&#6&\else\includegraphics[width=1cm]{#6}\fi
}

% Round profile picture
\newcommand{\roundpic}[1]{%
  \begin{tikzpicture}
    \clip (0,0) circle (2cm);
    \node at (0,0) {\includegraphics[width=4cm]{#1}};
  \end{tikzpicture}
}

% Icon with text
\newcommand{\icon}[3]{%
  % #1 = icon
  % #2 = color
  % #3 = additional styling
  {\color{#2}#1}%
}

% Set aside font color (for sidebar)
\newcommand{\setasidefontcolour}{%
  \color{black!70}%
}

% Paracol background options
\newcommand{\paracolbackgroundoptions}{%
  % Placeholder for background styling
}

\endinput
