# load packages -----------------------------------------------------------

library(readr)
library(dplyr)
library(stringr)
library(reshape2)
library(ggplot2)
library(ggthemes)


# load counts data --------------------------------------------------------

# project P43-12
local_fstats_file <- "data/P43-12_local_file_stats.csv"
local_fstats_dat <- read_csv(local_fstats_file) 
names(local_fstats_dat)[1] <- "lib_id"

globus_fstats_file <- "data/P43-12_globus_file_stats.csv"
globus_fstats_dat <- read_csv(globus_fstats_file) 
names(globus_fstats_dat)[1] <- "lib_id"

# temp filter
skip_libs <- c("lib6(832|924)")
local_fstats_dat <- local_fstats_dat %>% 
    filter(!str_detect(lib_id, skip_libs))

globus_fstats_dat <- globus_fstats_dat %>% 
    filter(!str_detect(lib_id, skip_libs))

# define fxns -------------------------------------------------------------

source("scripts/comparison_functions.R")

# compare file stats ------------------------------------------------------

fstats_comp_dat <- compare_dfs(local_fstats_dat,
                               globus_fstats_dat, norm_vals = TRUE)


# plot --------------------------------------------------------------------

fstats_comp_dat %>% 
    plot_compare_df()

