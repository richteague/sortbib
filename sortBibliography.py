import sys
from bibclasses import Bibliography

""" Convert a bibliography, sys.argv[1], into an ordered one. """

try:
    bib = Bibliography(sys.argv[1])
except:
    bib = Bibliography()

try:
    outname = sys.argv[2]
except:
    outname = None
bib.writeBibliography(fileout=outname)
