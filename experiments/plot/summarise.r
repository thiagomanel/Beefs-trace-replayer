library("plyr")
library("ggplot2")

Args <- commandArgs(TRUE)
file <- Args[1]

replay <- read.table(file, header = T)
attach(replay)

filter_clm <- c("original_client", "call", "stamp", "system", "sample")
agg <- ddply(replay, filter_clm, function (x) c(sum=sum(x$latency), mean=mean(x$latency)))

write.table(agg, paste(file, "ops.agg", sep = "."))
