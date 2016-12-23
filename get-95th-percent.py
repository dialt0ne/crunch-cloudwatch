#!/usr/bin/python
#
# get-95th-percent.py
#
# ATonns Fri Feb 15 10:36:15 EST 2013
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# NOTE: must have keys set with aks first

import boto
import datetime
import sys

# arg must be instance id
instanceId = sys.argv[1]

# what statistics you want
period = 60
metric_name = "CPUUtilization"
namespace = "AWS/EC2"
statistic = "Maximum"
dimension = {"InstanceId": instanceId}
unit = "Percent"
# how far back do you want to go?
total_days = 14
# what percentile do you want?
pct = 0.95

# connect to AWS
c = boto.connect_cloudwatch()
print "Getting " + metric_name + " for " + instanceId
count = 0
# where to collect stats
stats = []
# end of the period
end = datetime.datetime.now()
# iterate by day
day = 0
while day < total_days:
    # print out the current day
    sys.stdout.write(str(day))
    sys.stdout.flush()
    # set the period to be 1 day before the end
    start = end - datetime.timedelta(days=1)
    next_token = None
    # get the stats from aws for the specified period
    datapoints = c.get_metric_statistics(
        period, start, end, metric_name, namespace,
        {statistic}, dimension, unit)
    # for all the datapoints returned
    for d in datapoints:
        # add it to our list of stats
        stats.append(d[statistic])
        count += 1
        # pretty print some progress
        if count % 500 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
    # next time, end where this iteration started
    end = start
    day += 1
print "done."
# how many datapoints did we get?
l = len(stats)
# which one do we want?
n = int(l * pct)
# order the list
stats.sort()
# get it
val = stats[n]
print "Samples: " + str(l) + ", 95%=" + str(n) + ", Value=" + str(val)

# if you want to double check, change the False to True
if False:
    recount = 0
    # reiterate over the stats
    for i in stats:
        # make a special print for the 95th percentile
        if recount == n:
            print str(recount) + ":" + str(i) + " ***"
        # otherwise, normal print
        else:
            print str(recount) + ":" + str(i)
        recount += 1
