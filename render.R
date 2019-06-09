render_all <- function() {
    library(rmarkdown)

    # Set project root
    proj_root <- "C:/Users/kzms9/workspace/class"

    # Get all .Rmd files from project
    input_paths <- list.files(proj_root, pattern = ".Rmd", full.names = T, recursive = T)

    # Print info
    print("--------------- The following RMarkdown files will be rendered and placed in docs ---------------")
    for (i in 1:length(input_paths)) {
        print(paste(i, ". ", input_paths[i], sep = ""))
    }
    print("-------------------------------------------------------------------------------------------------")

    # Prepare output directories
    output_dirs <- sapply(input_paths, function(x){
        splt <- strsplit(x, "/")[[1]]
        sub(splt[length(splt)], "", sub("class", "class/docs", x))
    })

    # Render RMarkdown to HTML
    for (i in 1:length(input_paths)) {
        rmarkdown::render(
            input = input_paths[i],
            output_dir = output_dirs[[i]],
            clean = T,
            encoding = "UTF-8"
        )
    }

    return(output_paths)
}
render_all()