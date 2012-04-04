Args <- commandArgs(TRUE);

file=Args[1]


data <- read.table(file, header=F)
calls <- unique(data$V1)
for (call in calls) {
    print(call)
    sset = subset(data, data$V1 == call)
    print("trace latency")
    print(summary(sset$V3 - sset$V2))
    print("replay latency")
    print(summary(sset$V5 - sset$V4))
}
