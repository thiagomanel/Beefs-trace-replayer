library("ggplot2")

/*1319217042997604	2	conservative	abelhinha */
Args <- commandArgs(TRUE)
file=Args[1]

data <-read.table(file)
/*png(paste(file, ".png", sep=""))

min_stamp <- min(data$V1)

p <- ggplot(data, aes((data$V1 - min_stamp), data$V2))
p + geom_point(aes(colour = data$V3))*/

png(paste(file, ".png", sep=""))
b <- ggplot(data, aes(factor(data$V3), data$V2)) + facet_grid(. ~ data$V4)
b + geom_boxplot()
