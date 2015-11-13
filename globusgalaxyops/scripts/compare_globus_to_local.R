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

get_metric_stats <- function(metric_dat) {

    metric_name <- names(metric_dat)[1] %>% 
        str_extract(".*(?=\\.)")
    metric_dat <- sapply(metric_dat, as.numeric)
    x <- metric_dat[, 1]
    y <- metric_dat[, 2]
    

    metric_df <- data_frame(
        metric = metric_name,
        rho = cor.test(x, y)$estimate,
        eucd = eucd(x, y),
        rmsd = rmsd(x, y)
    )

    return(metric_df)
} 

# collect metric stats ----------------------------------------------------

metric_stats_dat <- lapply(as.list(2:length(local_metrics_dat)), 
                           function(x) { 
                               extract_metric(local_metrics_dat, 
                                              globus_metrics_dat, x) %>% 
                                   get_metric_stats
                           }) %>% 
    bind_rows()


# plot problem metrics ----------------------------------------------------

diff_metrics <- metric_stats_dat %>% 
    filter(log10(rmsd) > 0)

plot_metric_vals <- function(metric_name) {
    col <- which(names(local_metrics_dat) == metric_name)
    metric_dat <- extract_metric(local_metrics_dat, globus_metrics_dat, col,
                                 include_lib = TRUE)
    
    metric_melt <- metric_dat %>%
        melt(id.vars = "lib_id", variable.name = "metric_source")
    
    if (diff(range(metric_melt$value)) > 1e6) {
        p <- metric_melt %>% 
            ggplot(aes(x = lib_id, y = log10(value)))
    } else {
        p <- metric_melt %>% 
            ggplot(aes(x = lib_id, y = value))
    }
    
    p <- p +
        geom_point(aes(colour = metric_source), 
                   position = position_dodge(width = 0.5, height = 0))
}

dev.off()
lapply(as.list(diff_metrics$metric), plot_metric_vals)

# Bland-Altman plot

# n1 = as.name(names(metric_dat)[1])
# n2 = as.name(names(metric_dat)[2])
# dots = list(interp(~x - y, x = n1, y = n2),
#             interp(~(x + y) / 2, x = n1, y = n2))
# metric_dat %>% 
#     mutate_(.dots = setNames(dots, c("diff", "mean"))) %>% 
#     ggplot(aes(x = mean, y = diff)) +
#     geom_point()
