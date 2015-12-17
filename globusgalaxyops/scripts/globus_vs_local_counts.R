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

# pull out individual lib counts from each source
extract_lib <- function(local_df, globus_df, col, include_gene=FALSE) {
    lib_dat <- local_df %>% 
        select(one_of(names(.)[c(1, col)])) %>% 
        full_join(globus_df %>% 
                      select(one_of(names(.)[c(1, col)])),
                  by = c("geneName" = "geneName")) 
    
    if (!include_gene) {
        lib_dat <- lib_dat %>% 
            select(-geneName)
    }
    
    names(lib_dat) = names(lib_dat) %>% 
        str_replace("x", "local") %>% 
        str_replace("y", "globus")
    
    return(lib_dat)
}

# small custom function to calculate root mean squared error
rmsd <- function(x, y) {
    return(sqrt(mean(x - y)^2))
}

# small custom function to calculate euclidean distance
eucd <- function(x, y) {
    return(sqrt(sum((x - y)^2)))
}

# collect comparative stats for all metrics
get_lib_stats <- function(lib_dat, norm = FALSE) {
    
    lib_id <- names(lib_dat)[1] %>% 
        str_extract(".*(?=\\.)")
    lib_dat <- sapply(lib_dat, as.numeric)
    x <- lib_dat[, 1]
    y <- lib_dat[, 2]
    
    if (norm) {
        max_val <- max(x, y)
        x <- x / max_val
        y <- y / max_val
    }
    
    lib_df <- data_frame(
        lib = lib_id,
        rho = cor.test(x, y)$estimate,
        eucd = eucd(x, y),
        rmsd = rmsd(x, y),
        lm_int = lm(y ~ x)$coef[1],
        lm_slope = lm(y ~ x)$coef[2]
    )
    
    return(lib_df)
}

get_lm_stats <- function(x, y = NULL) {
    if (is.null(y)) {
        y <- x[[2]]
        x <- x[[1]]
    }
    
    s <- lm(x ~ y) %>% 
        summary() %>% 
        .[["coefficients"]] %>% 
        .[, 1:2] %>% 
        as.data.frame()
    
    row.names(s) <- c("int", "slope")
    names(s) <- c("est", "std_err")
    
    s <- s %>% 
        add_rownames(var = "lm_fit")
    return(s)
}

# pull out the relevant metric values from each source
compare_sampled_genes <- function(local_df, globus_df, sample_size = 1000) {
    sample_rows <- sample(1:nrow(local_df), sample_size)
    local_sample <- local_df %>% 
        slice(sample_rows)
    
    globus_sample <- globus_df %>% 
        slice(sample_rows)
    
    extract_lib(local_sample, globus_sample, 2) %>% 
        get_lm_stats() %>% 
        mutate(lib = names(local_df)[2])
}


# all correlations --------------------------------------------------------

remove_constant_vars <- function(data) {
    const_var_names <- sapply(data, n_distinct)
    const_var_names <- attr(const_var_names[const_var_names == 1], "names")
    data <- data[, !(names(data) %in% const_var_names)]    
    return(data)
}

local_metrics_mat <- local_metrics_dat %>% 
    select(-contains("HQ")) %>% # the Globus version of Picard does something
    # weird when it counts high quality bases;
    # ignore these fields for now
    remove_constant_vars() %>% 
    .[, -1] %>% 
    as.matrix()

globus_metrics_mat <- globus_metrics_dat %>% 
    select(-contains("HQ")) %>% 
    remove_constant_vars() %>%
    .[, -1] %>% 
    as.matrix()


# collect metric stats on remaining metrics -------------------------------

# pull out most meaningful metrics for comparison

sub_local_metrics_dat <- local_metrics_dat %>% 
    select(-contains("HQ")) %>% # the Globus version of Picard does something
    # weird when it counts high quality bases;
    # ignore these fields for now
    select(-contains("PF")) %>%
    remove_constant_vars()

sub_globus_metrics_dat <- globus_metrics_dat %>% 
    select(-contains("HQ")) %>%
    select(-contains("PF")) %>%
    remove_constant_vars()

metric_stats_dat <- lapply(as.list(2:length(sub_local_metrics_dat)), 
                           function(x) { 
                               extract_metric(sub_local_metrics_dat, 
                                              sub_globus_metrics_dat, x) %>% 
                                   get_metric_stats()
                           }) %>% 
    bind_rows()

metric_stats_norm_dat <- lapply(as.list(2:length(sub_local_metrics_dat)), 
                                function(x) { 
                                    extract_metric(sub_local_metrics_dat, 
                                                   sub_globus_metrics_dat, x) %>% 
                                        get_metric_stats(norm = TRUE)
                                }) %>% 
    bind_rows()



# select offset metrics ---------------------------------------------------

# pull out metrics with offset of > 1%
offset_metric_dat <- metric_stats_norm_dat %>% 
    filter(abs(lm_int) > 0.01)

# hq base check -----------------------------------------------------------

lib <- "lib6833"

gb <- globus_metrics_dat %>% filter(lib_id == lib) %>% .$PF_ALIGNED_BASES
lb <- local_metrics_dat %>% filter(lib_id == lib) %>% .$PF_ALIGNED_BASES
lbh <- local_metrics_dat %>% filter(lib_id == lib) %>% .$PF_HQ_ALIGNED_BASES
gbh <- globus_metrics_dat %>% filter(lib_id == lib) %>% .$PF_HQ_ALIGNED_BASES

