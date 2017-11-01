#!/usr/bin/perl 
#
# this script will generate redundant Fix formation
# written by ybyygu at 2005/6/2
#

die "You did not give Gaussian output file name as argument\n" if $#ARGV < 0;
die "You need only three parameter--Gaussian output file, start atom num, end atom num\n" if $#ARGV > 3;

$GAUOUT = $ARGV[0];
$startAN=$ARGV[1];
$endAN=$ARGV[2];

open(INPUT,"<$GAUOUT") || die "Could not open $GAUOUT\n";

$get=0;
@temp=();
$sl=0;		# $seperate line
while (<INPUT>) {
	if (/^\s*!\s+Name\s+Definition\s+Value/) {
	    	$get=1;
	    	next;
	}

	if ($get==1){
		if (/---------------/)	{
			$sl++;
			
			if ($sl==1){	# Begin of seperated infomation
				next;
			}
			
			if ($sl==2){
				$get=0;		# End of seperated infomation
				last;
			}		
		}
		
		if (/^\s*!\s+[ARDLXYZ]/){
			push(@temp,$_);
		}else{
			die "Is this a correct gaussian output file?";
		}
	}
}

close(INPUT);

#print @temp;

foreach $line (@temp){
	@t=split(/ +/,$line);
	
#	print $line;
	if (@t[3] =~ /R\((\S+),(\S+)\)/){
		if ($1>=$startAN && $1<=$endAN && $2>=$startAN && $2<=$endAN){
			print "B\t$1\t$2\tF\n";
		}else{
			next;
		}
	}elsif (@t[3] =~ /A\((\S+),(\S+),(\S+)\)/){
		if ($1>=$startAN && $1<=$endAN && $2>=$startAN && $2<=$endAN){
		    	if ( $3>=$startAN && $3<=$endAN ){
				print "A\t$1\t$2\t$3\tF\n";
		    	}
		}else{
			next;
		}
	}elsif (@t[3] =~ /D\((\S+),(\S+),(\S+),(\S+)\)/){
		if ($1>=$startAN && $1<=$endAN && $2>=$startAN && $2<=$endAN){
		    	if ($3>=$startAN && $3<= $endAN && $4>=$startAN && $4<=$endAN){
				print "D\t$1\t$2\t$3\t$4\tF\n";
		   	}
		}else{
			next;
		}
	}elsif (@t[3] =~ /L\((\S+),(\S+),(\S+),(\S+),(\S+)\)/){
		if ($1>=$startAN && $1<=$endAN && $2>=$startAN && $2<=$endAN){
		    	if ($3>=$startAN && $3<=$endAN && $4>=$startAN && $4<=$endAN){
				print "L\t$1\t$2\t$3\t$4\tF\n";
		    }
		}else{
			next;
		}
	}
	
#	print "@t[3]\n";
}

