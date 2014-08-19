#!/usr/bin/perl -ns
#
# utility to extract a value from an xml job property file
#

BEGIN {
	$main::prop || die("bad or missing prop");
}

chomp();
eval {print "$1\n"; exit 0;} if m/<name>${main::prop}.+<value>([^<]+)/;
