#!/usr/bin/env Rscript
library(ggplot2)
library(scales) # for muted function
args = commandArgs(trailingOnly=TRUE)

test = read.table(file=args[1],header=TRUE ,sep=",")
group.colors <- c("-" = "#dbdad2", "gRNA" = "#80c0e5", "PAM" ="#f79999", "Del" = "#000000", "Ins" = "#7f0114","Mut"="#f5f99f")
T = ggplot(test, aes(base_index,Profile)) +   geom_tile(aes(fill = factor(test$Char_stat)))  + theme_bw()  + theme(plot.margin= unit(c(1, 1, -1, 1), "lines")) + scale_x_continuous(expand=c(0,0)) +facet_grid(Row~Col)  +  scale_y_discrete(expand=c(0,0))+scale_fill_manual(values=group.colors)
ggsave(file = args[2], plot = T)
