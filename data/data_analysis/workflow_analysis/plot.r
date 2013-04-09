library("ggplot2")

Args <- commandArgs(TRUE)
file=Args[1]

event.load <-read.table(file, header=T)
# png(paste(file, ".png", sep=""))
# min_stamp <- min(data$V1)
# p <- ggplot(data, aes((data$V1 - min_stamp), data$V2))
# p + geom_point(aes(colour = data$V3))

png(paste(file, ".png", sep=""))
b <- ggplot(event.load, aes(factor(policy), count)) + geom_boxplot()
b + facet_wrap(~ machine, scales = "free")
