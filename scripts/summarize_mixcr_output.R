#!/usr/bin/env Rscript

# Generates summary csv of MiXCR data for a project
# accepts a path to a flowcell, identifies projects  
# that contain a 'mixcrOutput_trinity' folder, then 
# generates a mixcr_summary.csv file in the folder

#########################################################
# MiXCR loading functions, adapted from James Eddy's code
#########################################################
library(readr)
library(stringr)
library(dplyr)
library(purrr)
library(parallel)

mixcrOutputFolder <- "mixcrOutput_trinity"

# clean column names of data frame
clean_headers <- function(df) {
  headers <- names(df)
  headers <- str_to_lower(headers)
  headers <- str_replace_all(headers, "( )+", "_")
  headers <- str_replace_all(headers, "[^[:alnum:]_]", "_")
  headers <- str_replace_all(headers, "_+", "_")
  headers <- str_replace_all(headers, "_$", "")
  
  names(df) <- headers
  return(df)
}

# filter out unproductive TCR rearrangements
select_productive <- function(df) {
  new_df <- df[!grepl("[_|\\*]", df$junction) &
               !is.na(df$junction),]
  return(new_df)
}
 
# read IMGT results Summary from file
read_imgt_summary <- function(file) {
  imgt_df <- read_tsv(file) %>% 
    clean_headers() %>% 
    filter(functionality != "No results")
  
  return(imgt_df)
}

# parse raw IMGT clonotype results from Summary file
parse_imgt_summary <- function(imgt_df) {
  imgt_df %>% 
    select(sequence_id, v_gene_and_allele, v_region_score, v_region_identity_nt,
           j_gene_and_allele, j_region_score, j_region_identity_nt,
           aa_junction, 
           functionality, functionality_comment, junction_frame) %>% 
    mutate(v_gene = str_extract(v_gene_and_allele, 
                                "TR.*?(?=(\\*))"),
           v_region_score = as.integer(v_region_score),
           j_gene = str_extract(j_gene_and_allele, 
                                "TR.*?(?=(\\*))"),
           j_region_score = as.integer(j_region_score),
           junction = aa_junction) %>% 
    select(one_of("sequence_id", 
                  "v_gene", "v_region_score", "v_region_identity_nt",
                  "j_gene", "j_region_score", "j_region_identity_nt",
                  "junction",
                  "functionality", "functionality_comment", "junction_frame"))
  
}

# read and parse IMGT results from list of archive (.txz) files
read_imgt <- function(file_list = NULL, folder = NULL, 
                      sample_regex = "(lib|SRR)[0-9]+") {
  if(is.null(file_list) & is.null(folder)) {
    stop("Input must be provided for either `file_list` or `folder` argument.")
  }
  
  if(!is.null(folder)) {
    file_list <- list.files(folder, full.names = TRUE) %>% 
      .[str_detect(tolower(.), ".txz")]
  }
  
  if(!is.list(file_list)) {
    file_list <- as.list(file_list)
  }
  
  jxn_df <- mclapply(file_list, function(x) {
    extract_cmd <- sprintf("tar -xf '%s' -O '1_Summary.txt'", x)
    pipe(extract_cmd) %>% 
      read_file() %>% 
      read_imgt_summary() %>% 
      parse_imgt_summary() %>% 
      mutate(sequence_id = str_extract(sequence_id, sample_regex)) %>% 
      rename(sample = sequence_id)
  }) %>% 
    bind_rows()
  
  return(jxn_df %>% 
           arrange(sample))
}

# read MiXCR results from file
read_mixcr_clones <- function(file) {
  mixcr_df <- read_delim(file, delim = "\t") %>% 
    clean_headers()
}

# parse raw MiXCR clonotype results
parse_mixcr_clones <- function(mixcr_df) {
  tmp <<- mixcr_df
  mixcr_df %>% 
    transmute(cln_count = clonecount,
              full_nt_sequence = clonalsequence,
              v_gene = str_extract(allvhitswithscore,
                                   "[(TR)(IG)][A-Z]+[0-9]*(\\-[0-9])*(DV[0-9]+)*"),
              # note: not currently possible to get region overlap with
              # current version/parameters we use for MiXCR
              v_region_score = str_extract(allvhitswithscore, "(?<=\\()[0-9]+") %>% 
                as.integer(),
              v_align = allvalignments,
              j_gene = str_extract(alljhitswithscore, 
                                   "[(TR)(IG)][A-Z]+[0-9]*(\\-[0-9][A-Z]*)*"),
              j_align = alljalignments,
              j_region_score = str_extract(alljhitswithscore, "(?<=\\()[0-9]+") %>% 
                as.integer(),
              junction = as.character(aaseqcdr3)) %>% 
    rowwise() %>% 
    mutate(v_cd3_part_identity_nt = str_split(v_align, pattern = "\\|") %>% 
             map_int(function(x) {as.integer(x[length(x) - 2]) -
                 as.integer(x[length(x) - 3])}),
           v_cd3_part_score = str_split(v_align, pattern = "\\|") %>% 
             map_dbl(function(x) {as.numeric(x[length(x)])}),
           j_cd3_part_identity_nt = str_split(j_align, pattern = "\\|") %>% 
             map_int(function(x) {as.integer(x[length(x) - 2]) -
                 as.integer(x[length(x) - 3])}),
           j_cd3_part_score = str_split(j_align, pattern = "\\|") %>% 
             map_dbl(function(x) {as.numeric(x[length(x)])})) %>% 
    # select(one_of(c("full_nt_sequence","cln_count", "v_gene", 
    #                 "v_region_score", "v_cd3_part_score", 
    #                 "v_cd3_part_identity_nt", "j_gene", "j_region_score",
    #                 "j_cd3_part_score", "j_cd3_part_identity_nt", 
    #                 "junction")))
    select(one_of(c("full_nt_sequence", "v_gene",
                    "v_region_score", "v_cd3_part_score",
                    "v_cd3_part_identity_nt", "j_gene", "j_region_score",
                    "j_cd3_part_score", "j_cd3_part_identity_nt",
                    "junction")))
}

# read and parse MiXCR results from list of files
read_mixcr <- function(file_list = NULL, folder = NULL, 
                       sample_regex = "(lib|SRR)[0-9]+") {
  if(is.null(file_list) & is.null(folder)) {
    stop("Input must be provided for either `file_list` or `folder` argument.")
  }
  
  if(!is.null(folder)) {
    file_list <- list.files(folder, full.names = TRUE) %>% 
      .[str_detect(tolower(.), "clns.txt")]
  }
  
  if(!is.list(file_list)) {
    file_list <- as.list(file_list)
  }
  
  jxn_df <- mclapply(file_list, function(x) {
    if(file.size(x)) {
      mixcr_clones <- read_mixcr_clones(x)
      if (dim(mixcr_clones)[1] != 0){
        mixcr_clones %>% 
          parse_mixcr_clones() %>% 
          mutate(sample = str_extract(basename(x), sample_regex))
      }
    }
  }) %>% 
    bind_rows() %>% 
    select(one_of("sample", setdiff(names(.), "sample")))
  
  return(jxn_df %>% 
           select_productive() %>%
           arrange(sample))
}

#########################################################
# Helper functions
#########################################################
parse_project_name <- function(proj_folder){
  p <- str_extract(proj_folder, "P[0-9]+-[0-9]+")
  return(p)
}

# accepts a flow cell project folder path name with a Trinity folder,
# returns a list of all the libs in the Trinity folder
get_trinity_libs <- function(project_folder){
  all_trin_files <- list.files(file.path(project_folder, "Trinity"))
  trin_libs <- str_extract(all_trin_files, "lib[0-9]+")
  return(trin_libs)
}

# accepts a flow cell folder path name string
# returns a list of project folders that contain mixcrOutput_trinity
find_projects_with_mixcr <- function(fc_folder){
  libs_with_mixcr = NULL
  p_dirs <- list.files(fc_folder, pattern = "^Project_", full.names = TRUE)
  for (p_dir in p_dirs){
    mixcr_dir <- list.files(p_dir, pattern = paste0("^",mixcrOutputFolder))
    if(length(mixcr_dir) > 0) { 
      libs_with_mixcr <- c(libs_with_mixcr, p_dir)
    }
  }
  return(libs_with_mixcr)
}

#########################################################
# MiXCR functions
#########################################################
# validate that all of the Trinity outputs made it into MiXCR files
validate_mixcr_output <- function(proj_folder){
  trin_libs <- get_trinity_libs(proj_folder)
  mixcr_files <- list.files(file.path(proj_folder, mixcrOutputFolder))
  
  mixcr_file_suffixes <- 
    c("_mixcrAlign.vdjca",
      "_mixcrAlignPretty.txt",
      "_mixcrAssemble.clns",
      "_mixcrClns.txt",
      "_mixcrReport.txt")
  
  missing_files <- NULL
  for (lib in trin_libs){
    if(!is.na(lib)){
      for (suffix in mixcr_file_suffixes){
        srch_str <- paste0(lib, suffix)
        if(!any(str_detect(mixcr_files, srch_str))){
          missing_files <- c(missing_files, srch_str)
        }
      }
    }
  }
  
  if(!is.null(missing_files)){
    print("ERROR: The following files were expected but not found:")
    print(missing_files)
    return(FALSE)
  } else {
    return(TRUE)
  }
}

# generate a mixcr summary for a project folder containing 
# a mixcrOutput_trinity folder
make_mixcr_summary <- function(proj_folder){
  pname <- parse_project_name(proj_folder)
  currdate <- format(Sys.Date(), "%y%m%d")
  mixcr_file <- paste(pname, "mixcr_summary.csv", sep = "_")
  mixcr_jxns <- read_mixcr(folder = file.path(proj_folder, mixcrOutputFolder))
  if(nrow(mixcr_jxns) == 0){
    print(paste("WARNING: No junctions were detected in project", proj_folder))
    return(1)
  }
  write_csv(mixcr_jxns, file.path(proj_folder, mixcr_file))
  return(0)
}

# Run the program on a given flowcell path
run_prog <- function(fc_path){
  nFailedProjects <- 0
  project_paths <- find_projects_with_mixcr(fc_path)
  for (p in project_paths){
    if(validate_mixcr_output(p)){
      nFailedProjects <- 
        nFailedProjects +
        make_mixcr_summary(p) # returns 0 if success, 1 if failure
    }
  }
  if (nFailedProjects > 0){
    print(paste("WARNING: There were", nFailedProjects, "projects with issues."))
  }
}

#########################################################
# Main Program
#########################################################
# Read in the command line args and process the project

args = commandArgs(trailingOnly=TRUE)

if (length(args) == 0 || length(args) > 1) {
  stop("Exactly one flow cell path must be passed as an argument.", call.=FALSE)
}

fc_path <- args[1]
run_prog(fc_path)



