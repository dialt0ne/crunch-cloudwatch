## Crunch Cloudwatch

Some scripts that calculate useful metrics from [AWS CloudWatch](http://aws.amazon.com/cloudwatch/)

* get-95th-percent.py - get 95th percentile of CPU for an instance (fold, spindle and mutilate for other metrics)
* get-ec2-summary.py - get mean, median, maximum and 95th pertcentile for all metrics for some EC2 InstanceIDs
* `get-lambda-summary.py` - get mean, median, maximum and 95th pertcentile for all metrics for a Lambda function

```
$ get-lambda-summary.py --help
usage: get-lambda-summary.py [-h] [-d DAYS] [-p PERCENTILE] [-B] [-D]
                             function [function ...]

positional arguments:
  function              lambda function(s) to collect stats on

optional arguments:
  -h, --help            show this help message and exit
  -d DAYS, --days DAYS  days of data to get
  -p PERCENTILE, --percentile PERCENTILE
                        what percentile do you want to calculate
  -B, --botodebug       enable boto debugging (not enabled with -D)
  -D, --debug           output at debug level
```

### License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

