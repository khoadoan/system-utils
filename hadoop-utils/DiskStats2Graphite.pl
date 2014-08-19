#!/usr/bin/perl -ns
#
# takes GetDiskStats.sh output and formats for graphite
#

BEGIN {
	$main::prefix = "di.hadoop-cc.disk-stats" if !$main::prefix;
	$main::ts = ();
	%main::metrics = ();
}

chomp();
if(m/^START.+\s(\d+)$/) {
	# output current stats
	for my $m (keys(%main::metrics)) {
		print "${main::prefix}.${m}\t$main::metrics{$m}\t${main::ts}\n";
	}
	$main::ts = $1;
	%main::metrics = ();
} elsif(m/^DFS Used:\s+(\d+)/) {
	$main::metrics{"used_raw.dfs"} = $1;
} elsif(m/executing on (\d+(?:\.\d+){3})/) {
	$main::node = $1;
	$main::node =~ s/\./-/g;
} elsif(m/^(?:(?:\/[^\/]+)\/)?(\S+)\s+(\d+)\s+\d+%$/) {
	my $key = "used_raw.${main::node}.$1";
	$main::metrics{$key} = $2;
}
