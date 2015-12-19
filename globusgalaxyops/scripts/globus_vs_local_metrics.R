# load packages -----------------------------------------------------------

library(readr)
library(dplyr)
library(stringr)
library(reshape2)
library(ggplot2)
library(ggthemes)


# load metrics data --------------------------------------------------------

# project P43-12
local_metrics_file <- "data/P43-12_local_metrics.csv"
local_metrics_dat <- read_csv(local_metrics_file)
names(local_metrics_dat)[1] <- "lib_id"

globus_metrics_file <- "data/P43-12_globus_metrics.csv"
globus_metrics_dat <- read_csv(globus_metrics_file)
names(globus_metrics_dat)[1] <- "lib_id"

# temp filter
skip_libs <- c("lib6832", "lib6924")
local_metrics_dat <- local_metrics_dat %>% 
    filter(!(lib_id %in% skip_libs))

globus_metrics_dat <- globus_metrics_dat %>% 
    filter(!(lib_id %in% skip_libs))


# select target metrics ---------------------------------------------------

metrics_list <- c("MEAN_READ_LENGTH",
                  "MEDIAN_3PRIME_BIAS",
                  "MEDIAN_5PRIME_BIAS",
                  "MEDIAN_CV_COVERAGE",
                  "TOTAL_READS",
                  "UNPAIRED_READS_EXAMINED",
                  "total_reads_in_fastq_file")

# define fxns -------------------------------------------------------------

source("scripts/comparison_functions.R")

# filter metrics ----------------------------------------------------------

remove_constant_vars <- function(data) {
    const_var_names <- sapply(data, n_distinct)
    const_var_names <- attr(const_var_names[const_var_names == 1], "names")
    data <- data[, !(names(data) %in% const_var_names)]    
    return(data)
}

# pull out most meaningful metrics for comparison

sub_local_metrics_dat <- local_metrics_dat %>% 
    select(-contains("HQ")) %>% # the Globus version of Picard does something
    # weird when it counts high quality bases;
    # ignore these fields for now
    select(-contains("PF"))

sub_globus_metrics_dat <- globus_metrics_dat %>% 
    select(-contains("HQ")) %>%
    select(-contains("PF"))


# compare metrics ---------------------------------------------------------

metric_comp_dat <- compare_dfs(sub_local_metrics_dat,
                                sub_globus_metrics_dat, norm_comp = TRUE)


# select offset metrics ---------------------------------------------------

# pull out metrics with offset of > 1%
offset_metric_dat <- metric_comp_dat %>% 
    group_by(item) %>% 
    mutate(int = ifelse(lm_fit == "int", est, lag(est))) %>% 
    filter(abs(int) > 0.01) %>% 
    select(-int)

# hq base check -----------------------------------------------------------

lib <- "lib6833"

gb <- globus_metrics_dat %>% filter(lib_id == lib) %>% .$PF_ALIGNED_BASES
lb <- local_metrics_dat %>% filter(lib_id == lib) %>% .$PF_ALIGNED_BASES
lbh <- local_metrics_dat %>% filter(lib_id == lib) %>% .$PF_HQ_ALIGNED_BASES
gbh <- globus_metrics_dat %>% filter(lib_id == lib) %>% .$PF_HQ_ALIGNED_BASES


# plot --------------------------------------------------------------------

metric_comp_dat %>% 
    plot_compare_df()
    

# check individual lib ----------------------------------------------------

lib6924_dat <- extract_row(local_metrics_dat, globus_metrics_dat, 22, 
                           labels = c("local", "globus"), 
                           include_obsnames = TRUE) %>% 
    mutate(lib6924_local_char = sprintf("%s", lib6924.local), 
           lib6924_globus_char = sprintf("%s", lib6924.globus))

