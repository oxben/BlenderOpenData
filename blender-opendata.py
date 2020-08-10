#!/usr/bin/env python3

'''
Extract statistics from Blender Benchmark Opendata (https://opendata.blender.org/)
Author: Oxben <oxben@free.fr>

-*- coding: utf-8 -*-
'''

import getopt
import json
import os
import sys
from statistics import mean, median, pvariance, stdev


#target_os = ('Linux-64bit', 'Windows-64bit')
target_os = ('Linux-64bit',)
#target_os = ('Windows-64bit',)

target_devices = (
    'GeForce GTX 950',
    'GeForce GTX 1650 SUPER',
    'AMD Ryzen 5 1600 Six-Core Processor',
    'AMD Ryzen 5 3600 6-Core Processor',
)

#target_devices = ('AMD Ryzen 5 1600 Six-Core Processor',)
#target_devices = ('AMD Ryzen 5 3600 6-Core Processor',)
#target_devices = ('GeForce GTX 950', 'GeForce GTX 1650 SUPER', 'AMD Ryzen 5 1600 Six-Core Processor',)
#target_devices = ('AMD Ryzen 5 1600 Six-Core Processor', 'AMD Ryzen 5 3600 6-Core Processor',)

results = {} # results = { "koro" : [(,,), (,,)], "classroom": [(,,), (,,)]}


def parse_v1_v2(j):
    '''Parse v1 and v2 entry'''
    global results
    render_device = j['data']['device_info']
    render_device_name = render_device['compute_devices'][0]
    if type(render_device_name) is dict:
        # v2
        render_device_name = render_device['compute_devices'][0]['name']
    render_device_name = render_device_name.replace(' (Display)', '')
    os_name = j['data']['system_info']['system'] + '-' + j['data']['system_info']['bitness']
    blender_version = j['data']['blender_version']['version']

    if not render_device_name or not os_name:
        return

    if render_device_name in target_devices and os_name in target_os:
        for scene in j['data']['scenes']:
            if scene['stats']['result'] == 'OK':
                render_time = scene['stats']['total_render_time']
            else:
                continue

            scene_name = scene['name']
            if 'dist_name' in j['data']['system_info']:
                dist_name = j['data']['system_info']['dist_name'] + '-' + j['data']['system_info']['dist_version']
            else:
                dist_name = '-'

            # Add entry to results
            if not scene_name in results:
                results[scene_name] = []
            results[scene_name].append({'scene' : scene_name,
                                        'dev' : render_device_name,
                                        'os' : os_name,
                                        'dist': dist_name,
                                        'time': render_time,
                                        'version': blender_version})
            if not render_device_name:
                print(l)


def parse_v3(entry):
    '''Parse v3 entry'''
    global results

    for j in entry['data']:
        render_device = j['device_info']
        render_device_name = render_device['compute_devices'][0]['name']
        os_name = j['system_info']['system'] + '-' + j['system_info']['bitness']
        blender_version = j['blender_version']['version']

        if not render_device_name or not os_name:
            continue

        if render_device_name in target_devices and os_name in target_os:
            scene_name = j['scene']['label']
            render_time = j['stats']['total_render_time']
            if render_time <= 0:
                continue

            if 'dist_name' in j['system_info']:
                dist_name = j['system_info']['dist_name'] + '-' + j['system_info']['dist_version']
            else:
                dist_name = '-'

            # Add entry to results
            if not scene_name in results:
                results[scene_name] = []
            results[scene_name].append({'scene' : scene_name,
                                        'dev' : render_device_name,
                                        'os' : os_name,
                                        'dist': dist_name,
                                        'time': render_time,
                                        'version': blender_version})
            if not render_device_name:
                print(l)


def usage():
    '''Print program usage'''
    progname = os.path.basename(sys.argv[0])
    print(f"Usage: {progname} [-d render_device] [-o os] [-v] json_file")
    print("\nExamples:")
    print(f'    {progname} -o Linux-64bit -d "AMD Ryzen 5 3600 6-Core Processor" file.json')
    print("\nOS:")
    print("    Linux-64bit")
    print("    Windows-64bit")
    print("\nDevices:")
    print("    GeForce GTX 950")
    print("    GeForce GTX 1650 SUPER")
    print("    AMD Ryzen 5 1600 Six-Core Processor")
    print("    AMD Ryzen 5 3600 6-Core Processor")
    print("    AMD Ryzen 7 3700X 8-Core Processor")

#
# Main
#
if __name__ == "__main__":

    input_file = ""
    verbose = False

    # Parse args
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:o:v', ["help"])
    except getopt.GetoptError as err:
        print(err.msg)
        usage()
        sys.exit(1)

    for o, a in opts:
        if o == '-d':
            target_devices = (a,)
        elif o == '-o':
            target_os = (a,)
        elif o == '-v':
            verbose = True
        else:
            print("Error: unhandled option" + o)
            usage()
            sys.exit(1)

    if len(args) < 1:
        print("Error: missing input file")
        usage()
        sys.exit(1)

    input_file = args[0]

    # Parse all entries in json file
    with open(input_file) as f:
        lines = f.readlines()

        #print(json.dumps(json.loads(lines[0]), indent=4))

        for l in lines:
            j = json.loads(l)

            schema_version = j['schema_version']
            if schema_version in ('v1', 'v2'):
                parse_v1_v2(j)
            elif schema_version == 'v3':
                parse_v3(j)
            else:
                print('Unsupported schema : ' + schema_version)
                print(json.dumps(json.loads(l), indent=4))
                #sys.exit(1)

    # Sort results for each scene
    for scn in results.values():
        scn.sort(key=lambda res: res['time'])

    # Display results
    print(f"Target OS: {', '.join(target_os)}")
    print(f"Target Devices: {', '.join(target_devices)}")
    print("")
    for scn in sorted(results):
        print(f"Render time for '{scn}' (fastest to slowest):")
        times = []
        for r in results[scn]:
            if verbose:
                print(f"Scene: {r['scene']:20}  Device: {r['dev']:36}  RenderTime: {r['time']:10.2f}  OS: {r['os']}/{r['dist']:20}  V: {r['version']}")
            times.append(r['time'])
        print("Sample Count:             %10d" % len(times))
        print("Mean RenderTime:          %10.2f" % mean(times))
        print("Median RenderTime:        %10.2f" % median(times))
        print("Min RenderTime:           %10.2f" % min(times))
        print("Max RenderTime:           %10.2f" % max(times))
        if len(times) > 1:
            print("Std Deviation RenderTime: %10.2f" % stdev(times))
        #print("Variance RenderTime:     %10.2f" % pvariance(times))
        print("")
