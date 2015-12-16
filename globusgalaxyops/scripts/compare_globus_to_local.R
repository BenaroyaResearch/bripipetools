# load packages -----------------------------------------------------------

library(readr)
library(dplyr)
library(stringr)
library(reshape2)
library(ggplot2)


# load metrics data --------------------------------------------------------

# Project P43-12
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

extract_metric <- function(local_df, globus_df, col, include_lib=FALSE) {
    metric_dat <- local_df %>% 
        select(one_of(names(.)[c(1, col)])) %>% 
        full_join(globus_df %>% 
                      select(one_of(names(.)[c(1, col)])),
                  by = c("lib_id" = "lib_id")) 
    
    if (!include_lib) {
        metric_dat <- metric_dat %>% 
            select(-lib_id)
    }
    
    names(metric_dat) = names(metric_dat) %>% 
        str_replace("x", "local") %>% 
        str_replace("y", "globus")
    
    return(metric_dat)
}

rmsd <- function(x, y) {
    return(sqrt(mean(x - y)^2))
}

eucd <- function(x, y) {
    return(sqrt(sum((x - y)^2)))
}

get_metric_stats <- function(metric_dat, norm = FALSE) {

    metric_name <- names(metric_dat)[1] %>% 
        str_extract(".*(?=\\.)")
    metric_dat <- sapply(metric_dat, as.numeric)
    x <- metric_dat[, 1]
    y <- metric_dat[, 2]
    
    if (norm) {
        max_val <- max(x, y)
        x <- x / max_val
        y <- y / max_val
    }
    

    metric_df <- data_frame(
        metric = metric_name,
        rho = cor.test(x, y)$estimate,
        eucd = eucd(x, y),
        rmsd = rmsd(x, y),
        lm_int = lm(y ~ x)$coef[1],
        lm_slope = lm(y ~ x)$coef[2]
    )

    return(metric_df)
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
                                   get_metric_stats
                           }) %>% 
    bind_rows()

selected_metric_stats <- metric_stats_dat %>% 
    filter(metric %in% metrics_list)

metric_stats_norm_dat <- lapply(as.list(2:length(sub_local_metrics_dat)), 
                           function(x) { 
                               extract_metric(sub_local_metrics_dat, 
                                              sub_globus_metrics_dat, x) %>% 
                                   get_metric_stats(norm = TRUE)
                           }) %>% 
    bind_rows()



# select offset metrics ---------------------------------------------------

offset_metric_dat <- metric_stats_dat %>% 
    filter(abs(lm_int) > 0.1)

# simple metric plotting --------------------------------------------------

plot_metric <- function(metric, norm = FALSE, rank = FALSE, rm_outliers = FALSE) {
    x <- local_metrics_dat[[metric]]
    y <- globus_metrics_dat[[metric]]
    
    if (rank) {
        norm <- FALSE
        rm_outliers <- FALSE
        x <- rank(x)
        y <- rank(y)
    }
    
    if (norm) {
        max_val <- max(x, y)
        x <- x / max_val
        y <- y / max_val
    }
    
    if (rm_outliers) {
        q <- IQR(c(x, y))
        m <- median(c(x, y))
        x <- x[ (x >= (m - 0.75*q)) & (x <= (m + 0.75*q)) ]
        y <- y[ (y >= (m - 0.75*q)) & (y <= (m + 0.75*q)) ]
        print(m - 0.75*q)
        print(m + 0.75*q)
    }

    plot(x, y, main = metric, xlab = "local", ylab = "globus")
    abline(0, 1)
}

<<<<<<< HEAD
# hq base check -----------------------------------------------------------

lib <- "lib6833"

gb <- globus_metrics_dat %>% filter(lib_id == lib) %>% .$PF_ALIGNED_BASES
lb <- local_metrics_dat %>% filter(lib_id == lib) %>% .$PF_ALIGNED_BASES
lbh <- local_metrics_dat %>% filter(lib_id == lib) %>% .$PF_HQ_ALIGNED_BASES
gbh <- globus_metrics_dat %>% filter(lib_id == lib) %>% .$PF_HQ_ALIGNED_BASES
=======

# plot selected metrics ---------------------------------------------------

dev.off()
lapply(as.list(diff_metrics$metric), plot_metric_vals)
>>>>>>> 5fc329152a0ad33c15c0681543ccf4ac955216c7

lr <- local_metrics_dat %>% filter(lib_id == lib) %>% .$PF_READS_ALIGNED
gr <- globus_metrics_dat %>% filter(lib_id == lib) %>% .$PF_READS_ALIGNED
lrh <- local_metrics_dat %>% filter(lib_id == lib) %>% .$PF_HQ_ALIGNED_READS
grh <- globus_metrics_dat %>% filter(lib_id == lib) %>% .$PF_HQ_ALIGNED_READS

