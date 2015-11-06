# load packages -----------------------------------------------------------

library(readr)
library(dplyr)
library(stringr)
library(reshape2)
library(ggplot2)


# load data ---------------------------------------------------------------

# Project P43-12
local_metrics_file <- "data/P43-12_local_metrics.csv"
local_metrics_dat <- read_csv(local_metrics_file)
names(local_metrics_dat)[1] <- "lib_id"

globus_metrics_file <- "data/P43-12_globus_metrics.csv"
globus_metrics_dat <- read_csv(globus_metrics_file)
names(globus_metrics_dat)[1] <- "lib_id"


# combine data ------------------------------------------------------------

metric_dat <- local_metrics_dat %>% 
    select(one_of(names(.)[c(1, 3)])) %>% 
    full_join(globus_metrics_dat %>% 
                  select(one_of(names(.)[c(1, 3)])),
              by = c("lib_id" = "lib_id"))

names(metric_dat) = names(metric_dat) %>% 
    str_replace("x", "local") %>% 
    str_replace("y", "globus")

metric_dat %>% 
    ggplot(aes_q(x = as.name(names(.)[2]),
                 y = as.name(names(.)[3]))) +
    geom_point()