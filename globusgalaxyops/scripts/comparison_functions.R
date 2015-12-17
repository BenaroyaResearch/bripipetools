
# pull out matching column from two data frames
extract_col <- function(df1, df2, col, labels=c("1", "2"), 
                        include_rownames=FALSE) 
{
    col_names <- names(df1)[c(1, col)]
    key_name <- col_names[1]
    
    col_dat <- df1 %>% 
        select(one_of(col_names)) %>% 
        full_join(df2 %>% 
                      select(one_of(col_names)),
                  by = key_name) 
    
    if (!include_rownames) {
        col_dat <- col_dat %>% 
            select(-one_of(key_name))
    }
    
    names(col_dat) = names(col_dat) %>% 
        str_replace("x", labels[1]) %>% 
        str_replace("y", labels[2])
    
    return(col_dat)
}

# use lm estimates (intercept, slope) to compare two vectors
get_lm_stats <- function(x, y = NULL, norm = FALSE) {
    if (is.null(y)) {
        y <- x[[2]]
        x <- x[[1]]
    }
    
    if (norm) {
        max_val <- max(x, y)
        if (max_val > 0) {
            x <- x / max_val
            y <- y / max_val
        }
    }
    
    if (sum(x == y) == length(x) & n_distinct(x) == 1) {
        s <- data_frame(lm_fit = c("int", "slope"), 
                        est = c(0, 1),
                        std_err = c(0, 0))
    } else {
        s <- lm(x ~ y) %>% 
            summary() %>% 
            .[["coefficients"]] %>% 
            .[, 1:2] %>% 
            as.data.frame()
        
        row.names(s) <- c("int", "slope")
        names(s) <- c("est", "std_err")
        
        s <- s %>% 
            add_rownames(var = "lm_fit")
    }
    
    return(s)
}

# compare two dataframes column-by-column
compare_dfs <- function(df1, df2, norm_vals = FALSE) {
    col_nums = 2:ncol(df1)
    df_comp_dat <- lapply(as.list(col_nums), 
                          function(x) { 
                              col_name <- names(df1)[x]
                              print(col_name)
                              lm_dat <- extract_col(df1, df2, x) %>% 
                                  get_lm_stats(norm = norm_vals) %>% 
                                  mutate(col = col_name)
                              return(lm_dat)
                          }) %>% 
        bind_rows()
    return(df_comp_dat)
}