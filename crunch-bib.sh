#!/bin/sh

# Set common variables
. vars.sh

# Results directory
rm -r $RESULTS
mkdir -p $RESULTS

# Temporary directory
rm -r $TEMP
mkdir -p $TEMP

# Get approved GENI entries from Citeulike.
curl --user-agent "mberman/mberman@bbn.com wget-export" --output $RESULTS/geni-bibliography.bib $CITEGENI

# Get a listing of publications by year.
grep "year =" $RESULTS/geni-bibliography.bib | sort | uniq -c | tee $RESULTS/GENI-pubs-by-year.txt

# Preprocess some of the more egregious escaping errors out of the input stream. This is pretty hacky and could be a lot better.
cat $RESULTS/geni-bibliography.bib | sed -e 's/~{}/~/g' -e 's/\"{/####/g' -e 's/"/\\"/g' | sed -e 's/####/\"{/g' > $TEMP/preprocessed-bibliography

# Run preprocessed input file through bib2x to get a formatted listing of the publications, with full details.
cat $TEMP/preprocessed-bibliography | bib2x -t $FORMATS/geni-bib-full.late > $TEMP/pubs-full.html

# Run preprocessed input file through bib2x to get a formatted listing of the publications, in concise format.
cat $TEMP/preprocessed-bibliography | bib2x -t $FORMATS/geni-bib-concise.late > $TEMP/pubs-concise.html

# Run preprocessed input file through bib2x and additional post-processing to get a list of authors.
cat $TEMP/preprocessed-bibliography | bib2x -t $FORMATS/geni-authors.late | grep -v '^$' | sed 's/ and /$/g' | tr $ '\n' | sort | uniq | python ./process-authors.py | awk '{print "<li>",$0,"</li>"}' > $TEMP/authors.html

cat \
    $FORMATS/geni-bib-header.html \
    $TEMP/pubs-full.html \
    $FORMATS/geni-bib-divider1.html \
    $TEMP/pubs-concise.html \
    $FORMATS/geni-bib-divider2.html \
    $TEMP/authors.html \
    $FORMATS/geni-bib-trailer.html > $RESULTS/formatted-geni-bibliography.html
    
