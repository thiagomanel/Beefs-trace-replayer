# It plots a facet grid of scatter plots. The grid is faced by
# original client machine (traced machine names) and call (e.g. open, close)

# A point within each plot is the sum of response times recorded in each experiment repetition.
library("ggplot2")

Args <- commandArgs(TRUE)

#file is the output of summarise.r script
file <- Args[1]
data <- read.table(file, header = T, row.names = NULL)

#> summary(data)
#  row.names          original_client     call       stamp        system    
# Length:5612        abelhinha: 732   close :976   1day :1380   beefs:4232  
# Class :character   cherne   : 732   fstat :854   1min :1472   nfs  :1380  
# Mode  :character   mulato   : 732   llseek:854   30sec:1380               
#                    mussum   : 732   open  :976   None :1380               
#                    pepino   : 732   read  :976                            
#                    pitu     : 732   write :976                            
#                    (Other)  :1220                                         
#     sample           sum                 mean          
# Min.   : 0.00   Min.   :       42   Min.   :1.887e+00  
# 1st Qu.: 7.00   1st Qu.:    32302   1st Qu.:5.877e+01  
# Median :15.00   Median :   513429   Median :3.162e+02  
# Mean   :14.76   Mean   :  4765113   Mean   :6.247e+03  
# 3rd Qu.:22.00   3rd Qu.:  2340600   3rd Qu.:3.562e+03  
# Max.   :31.00   Max.   :411658043   Max.   :6.607e+06  
                                                        
attach(data)

p <- ggplot(data, aes(factor(stamp), sum)) + geom_point()
p + facet_grid(original_client~call)
p <- ggplot(data, aes(factor(stamp), sum)) + geom_point() + scale_y_log10()
p1 <- p + facet_grid(original_client~call, scales = "free_y")

ggsave(paste(file, "png", sep = "."), plot=p1)
