library("ggplot2")
Args <- commandArgs(TRUE);

file=Args[1]

data <- read.table(file, header=T)

p <- ggplot(data, aes(timestamp, num_ops))
a <- aggregate(data$num_ops, by=list(V1=data$timestamp), FUN="sum")

png(paste(file, ".png", sep=""))
p + geom_line(data=a, aes(x=V1,y=x)) + geom_point(data=data,aes(x=timestamp, y=num_ops,colour=machine))
