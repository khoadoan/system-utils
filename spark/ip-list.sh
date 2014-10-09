#!/bin/bash

hadoop dfsadmin -report | perl -ne 'print "$1\n" if m/^Name:\s+(\d+(?:\.\d+){3})/;'
