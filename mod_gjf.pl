#!/usr/bin/perl 
#
# this script will replace all mol-variable into const formation
# written by ybyygu at 2005/6/2
#

die "You did not give Gaussian input file name as argument\n" if $#ARGV < 0;
die "You need only one parameter --- Gaussian intput file name\n" if $#ARGV > 0;

$GJF = $ARGV[0];

open(INPUT,"<$GJF") || die "Could not open $GJF\n";
while(<INPUT>) {
    s/\r//;
    push(@temp,$_);

}
close(INPUT);

$str=join('',@temp);		    # put all lines into one string

@gjf_file=split(/\n\n/,$str);	# then we split into sections seperated by blank line

$sn=$#gjf_file+1;	        	# section numbers
die "Not a complete gaussian input file!" if $sn<=3;
				# At least, we need 4 sections
				# route section
				#+title section
				#+molcular specfication
				#+variable section
				
$gjf_descp=join("\n\n",@gjf_file[0,1]);
$gjf_remain=join("\n\n",@gjf_file[4..($sn-1)]);

#print $gjf_descp;
#print $gjf_remain;

@output=();
push(@output,"$gjf_descp\n\n");

@gjf_molspec=split("\n",@gjf_file[2]);
@gjf_var=split("\n",@gjf_file[3]);

#print join("\n",@gjf_molspec);
#print join("\n",@gjf_var);
#

foreach $line (@gjf_var){
    	if ($line =~ /^\s*(\w+)\s+([0-9.-]+)/){
	    	$var{$1}=$2;
	}else{
	    	die "Incorrect gjf file format!";
	}
}

$ln=0;
foreach $line (@gjf_molspec){
	$line =~ s/^\s+//;
	$line =~ s/\s+$//;
	@t=split /\s+/,$line;
    
    	if ($ln==2){
		if (@var{@t[2]}) {	
			$line =~ s/@t[2]/$var{@t[2]}/;
		}
	}elsif ($ln==3){
		if (@var{@t[2]}) {			
			$line =~ s/@t[2]/$var{@t[2]}/;
		}
		
		if (@var{@t[4]}) {						
			$line =~ s/@t[4]/$var{@t[4]}/;
		}
	}elsif ($ln > 3){
		if (@var{@t[2]}) {				
			$line =~ s/@t[2]/$var{@t[2]}/;
		}
		
		if (@var{@t[4]}) {				
			$line =~ s/@t[4]/$var{@t[4]}/;
		}
		
		if (@var{@t[6]}) {				
			$line =~ s/@t[6]/$var{@t[6]}/;
		}	
	}

	$ln++;
	
	if  ($ln!=1){
		$line =~ s/\s+/\t/g;
	}
	push(@output,"$line\n");	
}

push(@output,"\n");
push(@output,"$gjf_remain\n");

print @output;
