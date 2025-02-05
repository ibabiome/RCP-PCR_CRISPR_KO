#!/usr/bin/perl -w

use strict;
use Data::Dumper;


my $pth = shift;

my $seq_dir = shift; ##### FULL PATH REQIRED!
$seq_dir =~ s/\/$//g;

my @files = @ARGV; ##### FULL PATH REQUIRED; identified barcode dmp files in QC_and_BC/out.identification


for my $file (@files){
    print $file;
    if($file =~ /\/([^\/]+)\.dmp/){
	my $save_name = $1;
	open SAVE, '>'.$seq_dir.'/QC/sh.count/'."$save_name\.sh";
	
	my $command = 'perl ' .$pth.'count_read_v2.pl ' . "$file ";
	$command .= '> '.$seq_dir.'/QC/out.count/' . "$save_name\.dmp\n";
	
	print SAVE $command;
	
	close SAVE;	
    }
}

