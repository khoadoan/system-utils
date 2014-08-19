#!/bin/bash

function getDfsSlaves
{
	hadoop dfsadmin -report | perl -ne 'print "$1\n" if m/^Name:\s+(\d+(?:\.\d+){3})/;'
}

function getSlaves
{
	hadoop job -list-active-trackers | perl -ne 'print "$1\n" if m/tracker_(\d+(?:\.\d+){3})/;'
}
