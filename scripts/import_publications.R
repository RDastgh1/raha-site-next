#!/usr/bin/env Rscript

script_arg <- tryCatch(sys.frame(1)$ofile, error = function(e) NULL)
if (is.null(script_arg) || length(script_arg) == 0) {
  script_arg <- "scripts/import_publications.R"
}
script <- file.path(dirname(normalizePath(script_arg)), "import_publications.py")
if (!file.exists(script)) {
  script <- file.path("scripts", "import_publications.py")
}

args <- commandArgs(trailingOnly = TRUE)
status <- system2("python3", c(script, args))
quit(status = status)
