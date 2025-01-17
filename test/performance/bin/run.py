import sys
import time
import datetime
import argparse
import os
import glob
import subprocess
import json
import shutil
import urllib2

def run(profiler, dynamocli, test_case, test_output):
    # memlog DynamoCLI /o test.dyn
    # 
    # the output of memlog is cputime,managedheap,privateworkingset
    with open(test_output, "wb") as output: 
        for x in range(0, 3):
            proc = subprocess.Popen([profiler, dynamocli, '/o', test_case], stdout=output)
            proc.wait()
    
# harvest test case result from output_path 
# schema:
# {
#    'timestamp':'2016-01-01T09:45:00.000001',
#    'commits':[be581, abcd, ...],
#    'tag': 'RC1.0',
#    'testcases':
#    [ {'testcase':'foo', 'timestamp':'201001', 'cputime':'123', 'privatebytes':'21', 'managedheap':'22'},...]
# }
def harvest(test_result_path, output_path, commits, tag, logfile):
    current_time = datetime.datetime.now()
    timestamp = current_time.isoformat()
    benchmark_file = os.path.join(output_path, current_time.strftime("%Y%m%d%H%M%S") + '_benchmark.json')

    benchmark = {} 
    testcase_benchmarks = [] 
    benchmark['timestamp'] = timestamp
    benchmark['commits'] = commits 
    benchmark['tag'] = tag
    benchmark['testcases'] = testcase_benchmarks

    curdir = os.getcwd()
    os.chdir(test_result_path)
    for output in glob.glob("*.out"):
        try:
            results = []
            with open(output, 'r') as f:
                for line in f:
                    result = [int(x.strip()) for x in line.split(',')]
                    results.append(result)

            average_result = {} 
            for col in range(0, 3):
                value = 0
                rows = len(results)
                for row in range(0, rows):
                    value = value + results[row][col]
                value = value / rows
                average_result[col] = value

            testcase_benchmark = {}
            testcase_benchmark['testcase'] = os.path.splitext(output)[0]
            testcase_benchmark['timestamp'] = timestamp
            testcase_benchmark['cputime'] = average_result[0] 
            testcase_benchmark['managedheap'] = average_result[1] 
            testcase_benchmark['privatebytes'] = average_result[2] 
            testcase_benchmarks.append(testcase_benchmark)
        except:
            log(logfile, 'Failed at reading result of test ' + output)

    os.chdir(curdir)
    with open(benchmark_file, 'w') as data_file:
        data_file.write(json.dumps(benchmark, separators=(',', ':')))

    return benchmark_file

def log(logfile, msg):
    if logfile is None:
        print(msg)
        return
    else:
        f = open(logfile, 'a')
        f.write(msg + '\n')
        f.close()

def post_to_server(url, benchmark_file, key, logfile):
    from hashlib import sha1
    import hmac

    with open(benchmark_file, 'rb') as bf:
        jsondata = json.load(bf)
    data = json.dumps(jsondata, separators=(',', ':'))

    hashed = hmac.new(key, data, sha1)
    signature = hashed.digest().encode("hex").rstrip('\n')

    req = urllib2.Request(url, data, {'Content-Type': 'application/json', 'Content-Length':len(data), 'x-dynamo-signature':signature})
    try:
        resp = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        log(logfile, e)
    except urllib2.URLError as e:
        log(logfile, e)
    else:
        log(logfile, 'Send benchmark ' + benchmark_file + ' to server')

def main():
    parser = argparse.ArgumentParser(description="DesignScript performance test runner")
    parser.add_argument('-c', '--commits', nargs='*', type=str, required=False, help='commits')
    parser.add_argument('-g', '--tag', required=False, help='tag')
    parser.add_argument('-p', '--profiler', required=True, help='profiler path')
    parser.add_argument('-t', '--testcases', required=True, help='test case path')
    parser.add_argument('-r', '--dynamocli', required=True, help='DynamoCLI path')
    parser.add_argument('-o', '--output', required=True, help='output path')
    parser.add_argument('-l', '--logfile', required=False, help='log file path')
    args = parser.parse_args()

    logfile = args.logfile
    log(logfile, datetime.datetime.now().isoformat() + ' run performance benchmark')

    commits = args.commits
    if commits is None:
        commits = []

    tag = args.tag
    if tag is None:
        tag = ''

    profiler = args.profiler
    if not os.path.exists(profiler):
        log(logfile, 'Error: Profiler path ' + profiler + ' does not exists.')
        sys.exit(12)

    test_case_path = args.testcases
    if not os.path.exists(test_case_path):
        log(logfile, 'Error: Test cases path ' + test_case_path + ' does not exists.')
        sys.exit(12)

    dynamocli = args.dynamocli
    if not os.path.exists(dynamocli):
        log(logfile, 'Error: DynamoCLI ' + dynamocli + ' does not exists.')
        sys.exit(13)

    output_path = args.output
    if not os.path.exists(output_path):
        log(logfile, 'Error: Test output path ' + output_path + ' does not exist.')
        sys.exit(14)

    test_result_path = os.path.join(output_path, 'tmp')
    if not os.path.exists(test_result_path):
        os.mkdir(test_result_path)
    
    os.chdir(test_case_path)
    for dyn_file in glob.glob("*.dyn"):
        log(logfile, 'Running ' + dyn_file)
        dyn_file_path = os.path.join(test_case_path, dyn_file)
        test_case_name = os.path.splitext(dyn_file)[0]
        test_result_file = os.path.join(test_result_path, test_case_name + '.out')
        try:
            run(profiler, dynamocli, dyn_file_path, test_result_file) 
        except:
            log(logfile, 'Error: Failed to run test case ' + test_case_name)

    benchmark_file = harvest(test_result_path, output_path, commits, tag, logfile)
    shutil.rmtree(test_result_path)

    # get a signature
    url = os.environ.get('DYNAMO_BENCHMARK_SERVER')
    key = os.environ.get('DYNAMO_BENCHMARK_KEY')
    post_to_server(url, benchmark_file, key, logfile)
    log(logfile, 'Done')

if __name__ == "__main__":
    main()
