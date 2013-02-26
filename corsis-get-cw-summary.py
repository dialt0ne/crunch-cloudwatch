#!/usr/bin/python
#
# corsis-get-cw-summary.py
#
# ATonns Tue Feb 26 16:52:38 EST 2013
#
# Copyright 2013 Corsis
# http://www.corsis.com/
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
import logging
import sys

loglevel = logging.CRITICAL
# map metrics to units
units = {
    "CPUUtilization": "Percent",
    "DiskReadBytes": "Bytes",
    "DiskReadOps": "Count",
    "DiskWriteBytes": "Bytes",
    "DiskWriteOps": "Count",
    "NetworkIn": "Bytes",
    "NetworkOut": "Bytes",
    "DiskSpaceUtilization": "Percent",
    "MemoryUtilization": "Percent",
    "SwapUtilization": "Percent",
}
# what stat do we want?
statistic = "Maximum"
# how far back do you want to go?
total_days = 14
# what percentile do you want?
pct = 0.95

if __name__ == '__main__':
    # setup logging
    logging.basicConfig(
        format="corsis-get-cw-summary.py: %(message)s",
        level=loglevel)
    # when did we start?
    inittime = datetime.datetime.now()
    # print a header line
    print "instanceId,metric,mean,median,maximum,pertcentile"
    # args are instance IDs
    for instanceId in sys.argv[+1:]:
        logging.info("Instance ID: %s", instanceId)
        # what statistics you want
        dimension = {"InstanceId": instanceId}
        # connect to AWS
        c = boto.connect_cloudwatch()
        # get all the metrics for this instance
        next_token = ""
        for metric in c.list_metrics(next_token, dimension):
            # chop off "Metric:" from the name
            metric_name = str(metric)[7:]
            # do we care about this metric?
            if metric_name in units:
                logging.info("Getting metric: %s", metric_name)
                # units for this metric?
                unit = units[metric_name]
                # where to collect stats
                total = 0
                stats = []
                # end of the period
                end = inittime
                # iterate by day
                day = 0
                while day < total_days:
                    # set the period to be 1 day before the end
                    start = end - datetime.timedelta(days=1)
                    # get the stats from aws for the specified period
                    datapoints = metric.query(start, end, statistic, unit)
                    # for all the datapoints returned
                    for d in datapoints:
                        val = d[statistic]
                        # add it to our list of stats
                        stats.append(val)
                        total += val
                    # next time, end where this iteration started
                    end = start
                    day += 1
                # how many datapoints did we get?
                num = len(stats)
                # now order the list
                stats.sort()
                # what is the mean?
                meanval = total / num
                # which one do we want for the percentile?
                pctindex = int(num * pct)
                # get the percentile
                pctval = stats[pctindex]
                # which one do we want for the median?
                medindex = int(num * 0.50)
                # get the median
                medval = stats[medindex]
                # get the maximum
                maxval = stats[num - 1]
                # give it to the user
                print "%s,%s,%.3f,%.3f,%.3f,%.3f" % \
                    (instanceId, metric_name, meanval, medval, maxval, pctval)
