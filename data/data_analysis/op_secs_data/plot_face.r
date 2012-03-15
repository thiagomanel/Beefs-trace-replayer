library("ggplot2")

file="dados_juntos.txt"
data <- read.table(file, header=T)

data$timestamp = round(data$timestamp / (60*10^6))
png(paste(file, ".png", sep=""))

print(ggplot(data, aes(x=timestamp)) + geom_line(aes(y=num_ops), stat="summary", fun.y="sum") + geom_point(aes(y=num_ops, col=machine)) + facet_wrap(~ arquivo, scales="free_x"))
