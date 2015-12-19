
# pull out matching column from two data frames
extract_col <- function(df1, df2, col, labels=c("1", "2"), 
                        include_obsnames=FALSE) 
{
    var_names <- names(df1)[c(1, col)]
    obs_label <- var_names[1]
    
    col_dat <- df1 %>% 
        select(one_of(var_names)) %>% 
        full_join(df2 %>% 
                      select(one_of(var_names)),
                  by = obs_label) 
    
    if (!include_obsnames) {
        col_dat <- col_dat %>% 
            select(-one_of(obs_label))
    }
    
    names(col_dat) = names(col_dat) %>% 
        str_replace("x", labels[1]) %>% 
        str_replace("y", labels[2])
    
    return(col_dat)
}

transpose_df <- function(df) {
    # transpose the dataframe
    obs_names <- df[[1]]
    var_names <- names(df)[-1]
    df <- df[, -1] %>% 
        t() %>% 
        as.data.frame() %>% 
        bind_cols(data_frame(obs = var_names), .)
    names(df) <- c("obs", obs_names)
    return(df)
}

# pull out matching row from two data frames
extract_row <- function(df1, df2, row, labels=c("1", "2"), 
                        include_obsnames=FALSE) 
{
    df1 <- transpose_df(df1)
    df2 <- transpose_df(df2)
    
    var_names <- names(df1)[c(1, row)]
    obs_label <- var_names[1]
    
    row_dat <- df1 %>% 
        select(one_of(var_names)) %>% 
        full_join(df2 %>% 
                      select(one_of(var_names)),
                  by = obs_label) 
    
    if (!include_obsnames) {
        row_dat <- row_dat %>% 
            select(-one_of(obs_label))
    }
    
    names(row_dat) = names(row_dat) %>% 
        str_replace("x", labels[1]) %>% 
        str_replace("y", labels[2])
    
    return(row_dat)
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
compare_dfs <- function(df1, df2, norm_comp=FALSE, rowwise=FALSE, norm_cols=FALSE) {
    if (norm_cols) {
        df1 <- df1 %>% 
            mutate_each_(funs(. / max(.)), list(quote(-lib_id))) %>% 
            mutate_each(funs(ifelse(is.nan(.), 0, .)))
        
        df2 <- df2 %>% 
            mutate_each_(funs(. / max(.)), list(quote(-lib_id))) %>% 
            mutate_each(funs(ifelse(is.nan(.), 0, .)))
    }
    
    if (!rowwise) {
        col_nums = 2:ncol(df1)
        df_comp_dat <- lapply(as.list(col_nums), 
                              function(x) { 
                                  col_name <- names(df1)[x]
                                  lm_dat <- extract_col(df1, df2, x) %>% 
                                      get_lm_stats(norm = norm_comp) %>% 
                                      mutate(item = col_name)
                                  return(lm_dat)
                              }) %>% 
            bind_rows()
    } else {
        row_nums = 2:nrow(df1)
        df_comp_dat <- lapply(as.list(row_nums), 
                              function(x) {
                                  row_name <- df1[[1]][x]
                                  lm_dat <- extract_row(df1, df2, x) %>% 
                                      get_lm_stats(norm = norm_comp) %>% 
                                      mutate(item = row_name)
                                  return(lm_dat)
                              }) %>% 
            bind_rows()
    }

    return(df_comp_dat)
}

# plot matching column values from two dataframes against each other
# simple plot of metric values from one source vs the other
plot_compare_var <- function(df1, df2, col_name, 
                         norm = FALSE, rank = FALSE, rm_outliers = FALSE) 
{
    x <- df1[[col_name]]
    y <- df2[[col_name]]
    
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
    
    plot(x, y, main = col_name, xlab = "local", ylab = "globus")
    abline(0, 1)
}


# plot fxn ----------------------------------------------------------------

plot_compare_summary <- function(compare_dat, multi = FALSE) {
    
    spacer <- data_frame(item = rep(compare_dat$item[1], 4),
                         est = c(-0.1, 0.1, 0.9, 1.1),
                         lm_fit = c("int", "int", "slope", "slope"))
    
    p <- compare_dat %>% 
        ggplot(aes(x = item, y = est)) +
        geom_point(aes(size = std_err), fill = "black",
                   shape = 21, alpha = 0.7) +
        geom_blank(data = spacer)
    
    if (multi) {
        p <- p + 
            geom_boxplot(alpha = 0.5, outlier.shape = NA)
    }
    p <- p +
        facet_wrap(~ lm_fit, nrow = 2, scales = "free_y") +
        scale_fill_colorblind() +
        theme(axis.text.x = element_text(angle = -90, hjust = 0))
    return(p)
}

plot_compare_vars <- function(df1, df2, item_names) {
    item_cols = match(item_names, names(df1))
    
    item_dat <- lapply(as.list(item_cols), 
                       function(x) {
                           extract_col(df1, df2, x, labels = c("x", "y"))
                       }) %>% 
        bind_cols() %>% 
        bind_cols(df1[1], .)
    names(item_dat)[1] <- "obs"
    
    item_plot_dat <- item_dat %>% 
        melt(id.vars = "obs") %>% 
        extract(variable, c("item", "df_source"), regex = "(.*)\\.(.*)") %>% 
        spread(df_source, value) %>% 
        mutate(perc_diff = (x - y) / x) %>% 
        mutate(label = ifelse(perc_diff > 0.01, obs, ""))
    
    p <- item_plot_dat %>% 
        ggplot(aes(x = x, y = y)) + 
        geom_abline(intercept = 0, slope = 1) + 
        geom_point(aes(fill = perc_diff), shape = 21, size = 4, 
                   colour = "white", alpha = 0.7) +
        geom_text(aes(label = label), hjust = 0, vjust = 0, size = 4) +
        facet_wrap(~ item, scales = "free") +
        scale_x_continuous(expand = c(0.5, 0)) +
        scale_y_continuous(expand = c(0.5, 0))
    return(p)
}

