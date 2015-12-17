# load packages -----------------------------------------------------------

library(readr)
library(dplyr)
library(stringr)
library(reshape2)
library(ggplot2)


# load counts data --------------------------------------------------------

# project P43-12
local_counts_file <- "data/P43-12_local_counts.csv"
local_counts_dat <- read_csv(local_counts_file) %>% 
    select(one_of(sort(names(.))))

# transpose the dataframe
# gene_names <- local_counts_dat$geneName
# lib_ids <- names(local_counts_dat)[-1]
# local_counts_dat <- local_counts_dat[, -1] %>% 
#     t() %>% 
#     as.data.frame() %>% 
#     bind_cols(data_frame(lib_id = lib_ids), .)
# names(local_counts_dat) <- c("lib_id", gene_names)

globus_counts_file <- "data/P43-12_globus_counts.csv"
globus_counts_dat <- read_csv(globus_counts_file) %>% 
    select(one_of(sort(names(.))))

# temp filter
skip_libs <- c("lib6(832|924)")
local_counts_dat <- local_counts_dat %>% 
    select(-matches(skip_libs))

globus_counts_dat <- globus_counts_dat %>% 
    select(-matches(skip_libs))

# define fxns -------------------------------------------------------------

source("scripts/comparison_functions.R")

# pull out the relevant metric values from each source
compare_sampled_genes <- function(local_df, globus_df, sample_size = 10) {
    sample_rows <- sample(1:nrow(local_df), sample_size)
    local_sample <- local_df %>% 
        slice(sample_rows)
    
    globus_sample <- globus_df %>% 
        slice(sample_rows)
    
    comp_dat <- compare_dfs(local_sample, globus_sample)
    return(comp_dat)
}

# compare counts ----------------------------------------------------------

num_samples <- 100
counts_comp_dat <- lapply(as.list(1:num_samples), function(x) {
    compare_sampled_genes(local_counts_dat, globus_counts_dat)
}) %>% 
    bind_rows()


# plot --------------------------------------------------------------------

counts_comp_dat %>% 
    plot_compare_df(multi = TRUE)

