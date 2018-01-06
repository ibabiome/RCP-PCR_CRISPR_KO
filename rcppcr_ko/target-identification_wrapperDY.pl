#!/usr/bin/perl -w
use strict;
use Data::Dumper;

my $primers_fasta  = shift;
my $bar2num_file   = shift;
my $targets        = shift;


my $seq_dir = shift; ##### FULL PATH REQIRED!
$seq_dir =~ s/\/$//g;

my @files = @ARGV; ##### fragmented fasta files

my $mem;
for my $file (@files){
    my $name = 'N_A';
    if($file =~ /\/([^\/\.]+)\.[^\/\.]+$/){
	$name = $1;
    }
    $name =~ s/\_R2\_/\_R1\_/g;
    $mem->{$name} = 1;
}


for my $name (keys %$mem){
    my $R1_id     = $name;
    my $R2_id     = $name;
    my $save_name = $name;
    $R2_id =~ s/\_R1\_/\_R2\_/g;
    $save_name =~ s/\_R1\_/\_/g;

    open SAVE, '>'.$seq_dir.'/QC/sh.identification/'."$save_name\.sh";

    my $command = 'perl /home/t14905dy/projects/RCP-PCR/KO_clone/codes/get_target12082017.pl ' . "$primers_fasta $bar2num_file $targets $seq_dir $R1_id $R2_id ";
    $command .= '> '.$seq_dir.'/QC/out.identification/' . "$save_name\.dmp\n";

    print SAVE $command;

    close SAVE;
}
