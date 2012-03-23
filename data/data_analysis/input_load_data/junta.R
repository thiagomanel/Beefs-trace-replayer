library(foreach)

arquivos=c("2011_10_14", "2011_10_15", "2011_10_16", "2011_10_17", "2011_10_18", "2011_10_19", "2011_10_20", "2011_10_21")

df.junto = foreach(arquivo=arquivos, .combine=rbind) %do% {
	df = read.table(arquivo, header=TRUE)
	df$arquivo = arquivo
	df
}

write.table(df.junto, "dados_juntos.txt", quote=F, row.names=F)
