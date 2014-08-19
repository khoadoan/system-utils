#!/usr/bin/perl -ns
#
# extracts job status into tsv form from job logs
# ASSUME:  stats will be consistant across runs
#
# jobId,submitTime,launchTime,firstMapTaskLaunchTime,firstJobSetupTaskLaunchTime,firstJobCleanupTaskLaunchTime,finishTime,numMaps,numSlotsPerMap,numReduces,numSlotsPerReduce,user,queue,status,mapSlotSeconds,reduceSlotsSeconds,clusterMapCapacity,clusterReduceCapacity,jobName
#
BEGIN {
	$main::lineCnt = 0;
	@main::keys = ("DateHour", "jobId", "submitTime", "launchTime", "firstMapTaskLaunchTime", "firstJobSetupTaskLaunchTime", "firstJobCleanupTaskLaunchTime", "finishTime", "numMaps", "numSlotsPerMap", "numReduces", "numSlotsPerReduce", "user", "queue", "status", "mapSlotSeconds", "reduceSlotsSeconds", "clusterMapCapacity", "clusterReduceCapacity", "jobName")
}

chomp();
next if !m/^(\d+(?:[-:\s]\d+){3}).+?JobInProgress\$JobSummary.+:\s+(jobId=job_\d+_\d+(?:,[^=]+=[^,]+)+)/;
my $dateHour = $1;
my $stats = $2;
$dateHour =~ s/[\s:]/-/g;
print STDERR "${stats}\n" if $main::debug;
my %tuples = ("DateHour" => ${dateHour});
for my $tuple (split(/,/, ${stats})) {
	next if $tuple !~ m/(.+)=(.+)/;
	my $key = $1;
	my $val = $2;
	print STDERR "${key} => ${val}\n" if $main::debug;
	$tuples{$key} = ${val};
	$tuples{$key} = int($tuples{$key}/1000) if ${key} =~ m/Time/;
}
if($main::lineCnt++ == 0) {
	# print a header row
	print join("\t", @main::keys) . "\n";
}
print $tuples{"DateHour"};
for(my $i = 1; $i <= $#main::keys; $i++) {
	print "\t${tuples{$main::keys[$i]}}";
}
print "\n";
