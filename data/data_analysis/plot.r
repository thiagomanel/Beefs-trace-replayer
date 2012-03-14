p <- ggplot(data, aes(V1, V2))
a <- aggregate(data$V2, by=list(V1=data$V1), FUN="sum")
p + geom_line(data=a, aes(x=V1,y=x)) + geom_point(data=data,aes(x=V1, y=V2,colour=V3))
