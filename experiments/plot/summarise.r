library("plyr")
library("ggplot2")

Args <- commandArgs(TRUE)
file <- Args[1]

replay <- read.table(file, header = T)
attach(replay)

agg <- ddply(abelhinha, c("original_client", "system", "sample"), function (x) c(sum=sum(x$latency)))
