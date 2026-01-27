# Project latexmk configuration - prefer xelatex by default
$pdflatex = 'xelatex %O %S';
$latex = 'xelatex %O %S';
$pdf_mode = 1; # generate PDF
$clean_ext .= ' fdb_latexmk fls xdv';
