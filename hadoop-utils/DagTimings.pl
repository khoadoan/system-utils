#!/usr/bin/perl -ns
#
# merges job timings with DAG from job stderr
#

BEGIN {
	# load the job timings file
	open(FIN, "$main::jtf") || die("bad or missing job timing file (jtf)");
	%main::jobTimings = ();
	while(<FIN>) {
		next if !m/^(job_\d+_\d+)\s+(\d+)/;
		$main::jobTimings{$1} = $2;
		chomp();
	}
	close(FIN);
}

next if !m/^Job DAG:/;
# add timings for each job
print STDERR "found DAG\n" if $main::debug;
for(my $line = <>; $line =~ m/^job/; $line = <>) {
	$line =~ s/(job_\d+_\d+)/${1}\($main::jobTimings{$1}\)/g;
	print $line;
}
last;
