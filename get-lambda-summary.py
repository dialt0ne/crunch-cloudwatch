#!/usr/bin/env python
#
# get-lambda-summary.py
#
# ATonns Fri Dec 23 17:27:08 EST 2016
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

import argparse
import boto3
import datetime
import logging

loglevel = logging.CRITICAL
# map metrics to units
units = {
    "Invocations": {
        "units": "Count",
        "stat": "Sum",
    },
    "Errors": {
        "units": "Count",
        "stat": "Sum",
    },
    "DeadLetterError": {
        "units": "Count",
        "stat": "Sum",
    },
    "Duration": {
        "units": "Milliseconds",
        "stat": "Average",
    },
    "Throttles": {
        "units": "Count",
        "stat": "Sum",
    },
}


def create_parser(program_name):
    parser = argparse.ArgumentParser(prog=program_name)
    parser.add_argument(
        "-d", "--days", type=int,
        help="days of data to get",
        default=14,
    )
    parser.add_argument(
        "-p", "--percentile", type=float,
        help="what percentile do you want to calculate",
        default=0.95,
    )
    parser.add_argument(
        "-B", "--botodebug",
        help="enable boto debugging (not enabled with -D)",
        action="store_true"
    )
    parser.add_argument(
        "-D", "--debug",
        help="output at debug level",
        action="store_true",
    )
    parser.add_argument(
        'function',
        help='lambda function(s) to collect stats on',
        type=str, nargs='+',
    )
    return parser


if __name__ == '__main__':
    program_name = "get-lambda-summary.py"
    logging.basicConfig(
        level=loglevel,
        format='%(asctime)s %(filename)s %(levelname)s %(message)s',
    )
    parser = create_parser(program_name)
    args = parser.parse_args()

    # configure logging
    if args.debug:
        loglevel = logging.DEBUG
    root_logger = logging.getLogger('')
    root_logger.setLevel(loglevel)
    # set boto loglevel independently
    if args.botodebug:
        logging.getLogger('botocore').setLevel(logging.DEBUG)
        logging.getLogger('boto3').setLevel(logging.DEBUG)
    else:
        logging.getLogger('botocore').setLevel(logging.CRITICAL)
        logging.getLogger('boto3').setLevel(logging.CRITICAL)

    session = boto3.Session()
    client = session.client(service_name='cloudwatch')
    now = datetime.datetime.now()
    print "function,metric,mean,median,maximum,pertcentile"
    # args are function names
    for function_name in args.function:
        logging.debug("Function Name: %s", function_name)
        paginator = client.get_paginator('list_metrics')
        namespace = 'AWS/Lambda'
        dimensions = [{
            "Name": "FunctionName",
            "Value": function_name,
        }]
        pages = paginator.paginate(
            Namespace=namespace,
            Dimensions=dimensions,
        )
        for item in pages:
            for metric in item['Metrics']:
                metric_name = metric['MetricName']
                logging.debug("Metric Name: %s", metric_name)
                # do we care about this metric?
                if metric['MetricName'] in units:
                    logging.debug("Details: %s", metric)
                    statistic = units[metric_name]['stat']
                    unit = units[metric_name]['units']
                    total = 0
                    stats = []
                    end_time = now
                    day = 0
                    while day < args.days:
                        start_time = end_time - datetime.timedelta(days=1)
                        datapoints = client.get_metric_statistics(
                            Namespace=namespace,
                            MetricName=metric_name,
                            Dimensions=dimensions,
                            StartTime=start_time,
                            EndTime=end_time,
                            Period=60,
                            Statistics=[statistic],
                            Unit=unit,
                        )
                        for d in datapoints['Datapoints']:
                            # logging.debug("Datapoint: %s", d)
                            val = d[statistic]
                            stats.append(val)
                            total += val
                        # next time, end where this iteration started
                        end_time = start_time
                        day += 1
                    count = len(stats)
                    stats.sort()
                    mean_value = total / count
                    percent_index = int(count * args.percentile)
                    percent_value = stats[percent_index]
                    median_index = int(count * 0.50)
                    median_value = stats[median_index]
                    maximum_value = stats[count - 1]
                    print "%s,%s,%.3f,%.3f,%.3f,%.3f" % \
                        (function_name, metric_name, mean_value, median_value, maximum_value, percent_value)
