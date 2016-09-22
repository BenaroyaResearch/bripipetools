# load libraries ----------------------------------------------------------

library(readr)
library(dplyr)
library(ggplot2)
library(reshape2)
library(stringr)
library(ggthemes)
library(Biostrings)

# read adapter count file -------------------------------------------------

# adapter_count_file <- "data/adapter_contam.csv"
# adapter_count_dat <- read_csv(adapter_count_file) %>% 
#     .[, -1]

# read adapter seq file ---------------------------------------------------

adapter_seq_file <- "data/fastqc_adapter_seqs_151123.csv"
adapter_seq_dat <- read_csv(adapter_seq_file) %>% 
    .[, -1]


# filter projects of interest ---------------------------------------------

# keep_flowcells <- c("150625_D00565_0089_BHMMCMADXX",
                    # "150828_D00565_0095_BC6NRPANXX")
# keep_flowcells <- c("150729_D00565_0092_AC6VC6ANXX")
keep_flowcells <- c("151123_D00565_0099_BC81MLANXX")

adapter_seq_dat <- adapter_seq_dat %>% 
    filter(flowcell %in% keep_flowcells) %>% 
    mutate(lib_id = str_extract(lib_id, "lib[0-9]+"))

# extract adapter match lengths -------------------------------------------

adapter_seq_dat <- adapter_seq_dat %>% 
    mutate(len = ifelse(percent == 0, 0,
                        as.numeric(str_extract(match,
                                               "[0-9]+(?=bp)"))))



# write file --------------------------------------------------------------

contam_file <- "data/example_fastqc_seqs.csv"
write_csv(adapter_seq_dat, contam_file)
# check for PCR primer sequence -------------------------------------------

# primer_seq <- "CAAGCAGAAGACGGCATACGAGAT"
# # primer_seq <- "AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGA"
# primer_comp <- complement(DNAString(primer_seq)) %>% as.character()
# primer_rcomp <- reverseComplement(DNAString(primer_seq)) %>% as.character()
# 
# # adapter_seq_dat <- adapter_seq_dat %>% 
# #     mutate(has_primer = str_detect(primer_seq, seq),
# #            has_primer_comp = str_detect(primer_comp, seq),
# #            has_primer_rcomp = str_detect(primer_rcomp, seq))
# 
# 
# test_seq <- adapter_seq_dat %>%
#     filter(lib_id == "lib7400_HMMCMADXX") %>% 
#     select(seq) %>% 
#     as.character()
# 
# pairwiseAlignment(DNAString(primer_rcomp), DNAString(test_seq))

# summarize ---------------------------------------------------------------

# filter adapter hits
adapter_seq_filtered <- adapter_seq_dat %>% 
    mutate(match = str_replace(match, " \\(.*\\)", "")) %>% 
    group_by(lib_id, match) %>% 
    filter(percent == max(percent))

# summarize adapter hits per lib

adapter_seq_summary <- adapter_seq_filtered %>% 
    group_by(flowcell, project, lane, prep, lib_id) %>% 
    summarise(num_hits = sum(len > 0),
              mean_len = mean(len),
              mean_perc = mean(percent),
              total_count = sum(count),
              total_perc = sum(percent))



# plot adapter seq data ---------------------------------------------------

adapter_seq_summary %>% 
    # filter(flowcell != '150615_D00565_0087_AC6VG0ANXX') %>% 
    ggplot(aes(x = project, y = mean_perc)) +
    geom_point(aes(fill = prep, size = mean_len),
               shape = 21, alpha = 0.5,
               position = position_jitter(width = 0.3, height = 0)) +
    facet_wrap(~ flowcell, scales = "free_x", ncol = 2) +
    theme(axis.text.x = element_text(angle = -90, hjust = 0)) +
    scale_fill_colorblind()


# filter adapter seqs -----------------------------------------------------

cutoff <- 50
adapter_seq_summary <- adapter_seq_dat %>%
    mutate(len = as.numeric(str_extract(match, 
                                        "[0-9]+(?=bp)"))) %>% 
    filter(len > cutoff) %>% 
    group_by(flowcell, project, lib_id) %>% 
    summarise(num_adapters = n()) %>%
    ungroup() %>% 
    group_by(flowcell, project) %>% 
    summarise(num_libs_w_adapters_filtered = sum(num_adapters > 0))


# merge count data --------------------------------------------------------

adapter_dat <- left_join(adapter_count_dat, adapter_seq_summary) %>% 
    mutate(num_libs_w_adapters_filtered = ifelse(
        is.na(num_libs_w_adapters_filtered), 0, num_libs_w_adapters_filtered))
    
# plot adapter counts -----------------------------------------------------

adapter_dat %>% 
    mutate(percent_w_adapter = num_libs_w_adapters_filtered / num_libs) %>% 
    ggplot(aes(x = project, y = percent_w_adapter)) +
    geom_point(aes(fill = prep, size = num_libs), 
               shape = 21, alpha = 0.8) +
    facet_wrap(~ flowcell, scales = "free_x") +
    scale_color_colorblind() +
    scale_fill_colorblind() +
    theme(axis.text.x = element_text(angle = -90, hjust = 0)) +
    scale_size_continuous(range = c(4, 8), breaks = seq(0, 100, 20))
