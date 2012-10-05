library("plyr")
library("ggplot2")

Args <- commandArgs(TRUE)
file <- Args[1]

replay <- read.table(file, header = T)
attach(replay)

abelhinha <- subset(replay, original_client)
attach(abelhinha)
agg <- ddply(abelhinha, c("system", "sample"), function (x) c(sum=sum(x$latency)))

png(filename="replay.png")
p <- ggplot(agg, aes(factor(agg$system), agg$sum))
p + geom_boxplot()
