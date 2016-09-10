# sortbib
Quickly sort out bibliography files for LaTeX. 

## sortbibliography.py

Sorts the given LaTeX bibliography file into alphabetical order of the citekeys. The citekeys are given as `author_year` for a single author, `author1_author2_year` for two author papers and `author1_ea_year` for three or more authors. If there are more than one items with the same citekey, they are ordered by month and appended with `a`, `b`, `c` and so on. This makes it more readable when writing.

To run: `python sortbibliography.py bibliography.bib [newbibliography.bib]`
