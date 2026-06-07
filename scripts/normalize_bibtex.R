#!/usr/bin/env Rscript

# Placeholder for future BibTeX normalization rules.
# Keep this independent from archived package code and tune it around the
# publication fields the site actually needs.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  message("Usage: normalize_bibtex.R data/publications.bib")
  quit(status = 0)
}

message("Normalization scaffold ready for: ", args[[1]])
