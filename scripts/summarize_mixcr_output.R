#!/usr/bin/env Rscript

# Generates summary csv of MiXCR data for a project
# accepts a path to a flowcell, identifies projects  
# that contain a 'mixcrOutput_trinity' folder, then 
# generates a mixcr_summary.csv file in the folder

#########################################################
# MiXCR loading functions, adapted from James Eddy's code
# Upgraded to work with R version 4.x and to remove previously existing TCRs by Stephan Pribitzer
# Use database configuration file, Matt Lawrence
#########################################################
library(readr)
library(rlang)
library(stringr)
library(dplyr)
library(purrr)
library(parallel)
library(mongolite)

mixcrOutputFolder <- "mixcrOutput_trinity"

# Read in database config information
allArgs <- commandArgs(trailingOnly=FALSE)
scriptName <- sub("--file=", "", allArgs[grep("--file=", allArgs)])
scriptDir <- dirname(scriptName)
configFile <- file.path(scriptDir, "..", "bripipetools", "config", "default.ini")
config <- ini::read.ini(configFile)

# Open a connection to a collection in the research db
# collection: the name of the collection to access
resDbConnect <- function(collection){
  dbref <- mongo(collection,
                 db = config$researchdb$db_name,
                 url = paste0(
                   "mongodb://",
                   config$researchdb$user, ":",
                   config$researchdb$password, "@",
                   config$researchdb$db_host)
                 )
  return(dbref)
}

# Insert a dataframe of tcr data into the genomicsTCR collection
insertMixcrOutput <- function(tcrData){
  tcrDb <- resDbConnect("genomicsTCR")
  tcrDb$insert(tcrData)
  return(T)
}

# Check to see if a project ID exists in the genomicsTCR collection
checkMixcrProjectExists <- function(projId){
  tcrDb <- resDbConnect("genomicsTCR")
  result <- tcrDb$find(paste0('{"project":"', projId, '"}'), limit = 1)
  return(nrow(result) > 0)
}

removeMixcrProject <- function(projId) {
  tcrDb <- resDbConnect("genomicsTCR")
  result <- tcrDb$remove(paste0('{"project":"', projId, '"}'))
  return(T)
}

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

# mark which chains are unproductive, but only filter out "NA" junctions
mark_productive <- function(df) {
  new_df <- 
    df %>%
    dplyr::mutate(productive = ifelse(str_detect(junction, "[_|\\*]"), F, T)) %>%
    dplyr::filter(!is.na(junction))
  return(new_df)
}

# read MiXCR results from file
read_mixcr_clones <- function(file) {
  mixcr_df <- suppressMessages(read_delim(file, delim = "\t")) %>% 
    clean_headers()
}

# parse raw MiXCR clonotype results
parse_mixcr_clones <- function(mixcr_df) {
  # handle different versions of MiXCR that change names of columns
  seq_col_name <- ifelse("clonalsequence" %in% names(mixcr_df),
                         "clonalsequence", 
                         "targetsequences")
  mixcr_df %>% 
    transmute(cln_count = clonecount,
              full_nt_sequence = !!parse_expr(seq_col_name),
              v_gene = str_extract(allvhitswithscore,
                                   "[(TR)(IG)][A-Z]+[0-9]*(\\-[0-9]+)*(DV[0-9]+)*"),
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
              c_gene = str_extract(allchitswithscore, "[(TR)(IG)][A-Z]+[0-9]*(\\-[0-9][A-Z]*)*"),
              c_region_score = str_extract(allchitswithscore, "(?<=\\()[0-9]+") %>% as.integer(),
              c_align = allcalignments,  
              junction = as.character(aaseqcdr3),
              cdr3_nt_sequence = nseqcdr3) %>% 
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
    select(one_of(c(
          "full_nt_sequence","cdr3_nt_sequence", "v_gene", "v_region_score", "v_cd3_part_score", "v_cd3_part_identity_nt",
          "j_gene", "j_region_score", "j_cd3_part_score", "j_cd3_part_identity_nt",
          "c_gene", "c_region_score", "c_align",
          "junction"
        )))

}


# read and parse the MiXCR metadata from a mixcrReport file
read_mixcr_metadata <- function(folder, sample_regex = "(lib|SRR)[0-9]+"){
  file_list <- list.files(folder, full.names = TRUE) %>% 
    .[str_detect(tolower(.), "mixcrreport.txt")]
  
  metadata_df <- NULL
  for (curr_report in file_list){
    if(file.size(curr_report)){
      curr_metadata <- list(libid = str_extract(basename(curr_report), sample_regex))
      # read file line by line to parse
      # This is not efficient, but protects against giant files breaking things.
      curr_fcon <- file(curr_report, "r")
      while(T){
        curr_line <- readLines(curr_fcon, n = 1)
        if (length(curr_line) == 0){
          break
        }
        # check for metatdata in line
        curr_version <- 
          str_extract(curr_line, "^Version: [0-9,\\.]+") %>%
          str_replace("^Version: ", "")
        if(!is.na(curr_version)){curr_metadata$mixcrVersion <- curr_version}
        
        curr_lib <- 
          str_extract(curr_line, "lib=[a-zA-Z0-9\\.]+") %>%
          str_replace("lib=", "")
        if(!is.na(curr_lib)){curr_metadata$libVersion <- curr_lib}
        
        curr_args <- 
          str_extract(curr_line, "^Command line arguments: .+") %>% 
          str_replace("^Command line arguments: ", "")
        
        if(!is.na(curr_args)){
          curr_parsed_args <- parse_command_line_args(curr_args)
          if(curr_parsed_args$cmd == "align"){
            curr_species <- curr_parsed_args$s
            curr_metadata$species <- ifelse(is.null(curr_species), "hsa", curr_species)
            
            curr_chain <- ifelse(is.null(curr_parsed_args$c), 
                                 curr_parsed_args$l, 
                                 curr_parsed_args$c)
            curr_metadata$chainType <- ifelse(is.null(curr_chain), "default", curr_chain)
            
            curr_aligner <- curr_parsed_args$p
            curr_metadata$aligner <- ifelse(is.null(curr_aligner), "default", curr_aligner)
          }
        }
      }
      close(curr_fcon)
      
      if(is.null(curr_metadata$mixcrVersion)){ curr_metadata$mixcrVersion <- "< 2.1.3" }
      if(is.null(curr_metadata$libVersion)){curr_metadata$libVersion <- "unknown" }

      metadata_df <- rbind(metadata_df, data.frame(curr_metadata))
    }
  }
  return(metadata_df)
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
  
  # make sure there was mixcr data for the project
  if(nrow(jxn_df) == 0){
    print(paste("WARNING: No chains identified for project."))
    return(jxn_df)
  }
  
  return(jxn_df %>% 
           # include all chains, including unproductive, but mark which are productive
           mark_productive() %>%
           rename(libid = sample) %>% 
           arrange(libid))
}

#########################################################
# Helper functions
#########################################################
parse_project_name <- function(proj_folder){
  p <- str_extract(proj_folder, "P[0-9]+-[0-9]+")
  return(p)
}

# accepts a string representing a command with arguments (eg: "cmd -c cVal")
# returns a named list containing the arguments (eg: list(cmd="cmd", c="cVal"))
# Flags that don't take an argument will be in the list with "NA" values
parse_command_line_args <- function(cmd_string){
  split_cmd <- str_split(cmd_string, " -")[[1]]
  arg_list <- list(cmd = split_cmd[1])
  for (arg in split_cmd[-1]){
    split_arg = str_split(arg, " ")[[1]]
    arg_list[split_arg[1]] <- split_arg[2]
  }
  return(arg_list)
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
make_mixcr_summary <- function(proj_folder, lib_type, forceRemove=FALSE){
  pname <- parse_project_name(proj_folder)
  currdate <- format(Sys.Date(), "%y%m%d")
  mixcr_file <- paste(pname, currdate, "mixcr_summary.csv", sep = "_")
  mixcr_jxns <- read_mixcr(folder = file.path(proj_folder, mixcrOutputFolder))
  if(nrow(mixcr_jxns) == 0){
    print(paste("WARNING: No junctions were detected in project", proj_folder))
    return(1)
  }
  # add in metadata
  mixcr_metadata <- read_mixcr_metadata(folder = file.path(proj_folder, mixcrOutputFolder))
  mixcr_jxns <- left_join(mixcr_jxns, mixcr_metadata, by = "libid")
  write_csv(mixcr_jxns %>% dplyr::filter(productive) %>% dplyr::select(-productive), 
            file.path(proj_folder, mixcr_file))
  
  # add timestamp, project, and run ID columns
  currTime <- Sys.time()
  runId <- str_extract(proj_folder, "[0-9]{6}_D00565_[0-9]{4}_[A-Z0-9]+(XX|XY|X2)")
  projId <- str_extract(proj_folder, "P[0-9]+-[0-9]+")
  mixcr_jxns$dateCreated <- currTime
  mixcr_jxns$project <- projId
  mixcr_jxns$run <- runId
  mixcr_jxns$libType <- lib_type
  
  # push mixcr information to research database
  if(checkMixcrProjectExists(projId)){
    if (forceRemove) {
      print(paste("WARNING: Removing previous TCR collection for project", projId))
      removeMixcrProject(projId)
      print(paste("Data for project", projId, "are summarized and being pushed to the TCR database."))
      insertMixcrOutput(tcrData = mixcr_jxns)
    } else {
      print(paste("WARNING: Could not push data for project", projId, "to the TCR database, because it already exists."))
    }
  } else {
    print(paste("Data for project", projId, "are summarized and being pushed to the TCR database."))
    insertMixcrOutput(tcrData = mixcr_jxns)
  }
  return(0)
}

# Run the program on a given flowcell path
run_prog <- function(fcPath, libType, forceRemove=FALSE){
  nFailedProjects <- 0
  if (str_detect(fcPath, "/Project_")) {
    project_paths <- fcPath
  } else {
    project_paths <- find_projects_with_mixcr(fcPath)
  }
  for (p in project_paths){
    if(validate_mixcr_output(p)){
      nFailedProjects <- 
        nFailedProjects +
        make_mixcr_summary(p, libType, forceRemove) # returns 0 if success, 1 if failure
    } else {
      nFailedProjects <- nFailedProjects + 1
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

if (length(args) == 0 || length(args) > 2) {
  stop("One flow cell path must be passed as an argument with an optional '-bulk' flag.", call.=FALSE)
}

if (length(args) == 2 & !("-bulk" %in% args)) {
  stop("One flow cell path must be passed as an argument with an optional '-bulk' flag.", call.=FALSE)
}

fcPath <- args[args != "-bulk"]
libType <- ifelse(("-bulk" %in% args), "bulk", "single cell")
forceRemove <- TRUE

run_prog(fcPath, libType, forceRemove)

