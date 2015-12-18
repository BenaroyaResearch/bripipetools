# load packages -----------------------------------------------------------

library(readr)
library(dplyr)
library(stringr)
library(reshape2)
library(ggplot2)
library(rCharts)



# define fxns -------------------------------------------------------------

source("../tcrSeqAnalysis/R/prep_junctions.R")
source("../tcrSeqAnalysis/R/inspect_tcrs.R")


# load data ---------------------------------------------------------------

# local results first
mixcr_folder <- paste0("/Volumes/genomics/Illumina/",
                       "GLOBUS_TESTING_150615_D00565_0087_AC6VG0ANXX/",
                       "Project_P43-12Processed_151021/",
                       "mixcrOutput_trinity")
project <- "P43-12_local"
out_folder <- "data/"

# combine MiXCR junctions into a single file; read, format, and filter junctions
mixcr_local <- combine_mixcr_outputs(mixcr_folder, out_folder, project) %>% 
    format_mixcr_jxns() %>% 
    filter_mixcr_jxns() %>% 
    list(jxns = .)

# globus results
mixcr_folder <- paste0("/Volumes/genomics/Illumina/",
                       "150615_D00565_0087_AC6VG0ANXX/",
                       "gProject_P43-12Processed_151013_formatted/",
                       "mixcrOutput_trinity/")
project <- "P43-12_globus"
out_folder <- "data/"

# combine MiXCR junctions into a single file; read, format, and filter junctions
mixcr_globus <- combine_mixcr_outputs(mixcr_folder, out_folder, project) %>% 
    format_mixcr_jxns() %>% 
    filter_mixcr_jxns() %>% 
    list(jxns = .)


# construct TCRs ----------------------------------------------------------

mixcr_local[["tcrs"]] <- mixcr_local$jxns %>% 
    select_top_jxns(allow_multi = TRUE) %>% 
    construct_tcrs(any = TRUE)

mixcr_globus[["tcrs"]] <- mixcr_globus$jxns %>% 
    select_top_jxns(allow_multi = TRUE) %>% 
    construct_tcrs(any = TRUE)


# plot TCRs ---------------------------------------------------------------

# combine local and globus TCRs
local_globus <- mixcr_local$tcrs %>% 
    mutate(tcr_source = "IMGT") %>% 
    bind_rows(mixcr_globus$tcrs %>% 
                  mutate(tcr_source = "MiXCR")) %>% 
    list(tcrs = .)

# construct and display a sankey network linking libs to genes to junctions
local_globus[["plot"]] <- 
    build_sankey_network(local_globus$tcrs, 
                         chain = "both") %>% 
    build_sankey_plot(sankey_height = 440)
# local_globus$plot



# test --------------------------------------------------------------------

t2 %>% 
    # mutate(trav_gene = ifelse(is.na(trav_gene), "none", trav_gene))
    mutate_each(funs(ifelse(is.na(.), "none", .)))
