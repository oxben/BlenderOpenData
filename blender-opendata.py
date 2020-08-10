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


#DFLT_TARGET_OS = ('Linux-64bit', 'Windows-64bit')
DFLT_TARGET_OS = ('Linux-64bit',)
#DFLT_TARGET_OS = ('Windows-64bit',)

DFLT_TARGET_DEVICES = (
    'GeForce GTX 950',
    'GeForce GTX 1650 SUPER',
    'AMD Ryzen 5 1600 Six-Core Processor',
    'AMD Ryzen 5 3600 6-Core Processor',
)

#DFLT_TARGET_DEVICES = ('AMD Ryzen 5 1600 Six-Core Processor',)
#DFLT_TARGET_DEVICES = ('AMD Ryzen 5 3600 6-Core Processor',)
#DFLT_TARGET_DEVICES = ('GeForce GTX 950', 'GeForce GTX 1650 SUPER', 'AMD Ryzen 5 1600 Six-Core Processor',)
#DFLT_TARGET_DEVICES = ('AMD Ryzen 5 1600 Six-Core Processor', 'AMD Ryzen 5 3600 6-Core Processor',)

class BlenderOpenDataParser:
    '''Parser for exploring Blender Benchmark Open Data json files'''

    def __init__(self):
        self.target_os = DFLT_TARGET_OS
        self.target_devices = DFLT_TARGET_DEVICES
        self.results = {} # results = { "koro" : [(,,), (,,)], "classroom": [(,,), (,,)]}
        self.verbose = False


    def usage(self):
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


    def parse_v1_v2(self, entry):
        '''Parse v1 and v2 entry and insert matching data in results'''
        render_device = entry['data']['device_info']
        render_device_name = render_device['compute_devices'][0]
        if isinstance(render_device_name, dict):
            # v2
            render_device_name = render_device['compute_devices'][0]['name']
        render_device_name = render_device_name.replace(' (Display)', '')
        os_name = entry['data']['system_info']['system'] + '-' + entry['data']['system_info']['bitness']
        blender_version = entry['data']['blender_version']['version']

        if not render_device_name or not os_name:
            return

        if render_device_name in self.target_devices and os_name in self.target_os:
            for scene in entry['data']['scenes']:
                if scene['stats']['result'] == 'OK':
                    render_time = scene['stats']['total_render_time']
                else:
                    continue

                scene_name = scene['name']
                if 'dist_name' in entry['data']['system_info']:
                    dist_name = entry['data']['system_info']['dist_name'] + '-' + \
                                entry['data']['system_info']['dist_version']
                else:
                    dist_name = '-'

                # Add entry to results
                if not scene_name in self.results:
                    self.results[scene_name] = []
                self.results[scene_name].append({'scene' : scene_name,
                                                 'dev' : render_device_name,
                                                 'os' : os_name,
                                                 'dist': dist_name,
                                                 'time': render_time,
                                                 'version': blender_version})


    def parse_v3(self, entry):
        '''Parse v3 entry and insert matching data in results'''
        for d in entry['data']:
            render_device = d['device_info']
            render_device_name = render_device['compute_devices'][0]['name']
            os_name = d['system_info']['system'] + '-' + d['system_info']['bitness']
            blender_version = d['blender_version']['version']

            if not render_device_name or not os_name:
                continue

            if render_device_name in self.target_devices and os_name in self.target_os:
                scene_name = d['scene']['label']
                render_time = d['stats']['total_render_time']
                if render_time <= 0:
                    continue

                if 'dist_name' in d['system_info']:
                    dist_name = d['system_info']['dist_name'] + '-' + \
                                d['system_info']['dist_version']
                else:
                    dist_name = '-'

                # Add entry to results
                if not scene_name in self.results:
                    self.results[scene_name] = []
                self.results[scene_name].append({'scene' : scene_name,
                                                 'dev' : render_device_name,
                                                 'os' : os_name,
                                                 'dist': dist_name,
                                                 'time': render_time,
                                                 'version': blender_version})


    def print_results(self):
        '''Compute some statistics and print the results'''
        # Sort results for each scene
        for scn in self.results.values():
            scn.sort(key=lambda res: res['time'])

        # Display results
        print(f"Target OS: {', '.join(self.target_os)}")
        print(f"Target Devices: {', '.join(self.target_devices)}")
        print("")
        for scn in sorted(self.results):
            print(f"Render time for '{scn}' (fastest to slowest):")
            times = []
            for r in self.results[scn]:
                if self.verbose:
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


    def run(self):
        '''Main routine'''
        input_file = ""

        # Parse args
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'd:o:v', ["help"])
        except getopt.GetoptError as err:
            print(err.msg)
            self.usage()
            sys.exit(1)

        for o, a in opts:
            if o == '-d':
                self.target_devices = (a,)
            elif o == '-o':
                self.target_os = (a,)
            elif o == '-v':
                self.verbose = True
            else:
                print("Error: unhandled option" + o)
                self.usage()
                sys.exit(1)

        if len(args) < 1:
            print("Error: missing input file")
            self.usage()
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
                    self.parse_v1_v2(j)
                elif schema_version == 'v3':
                    self.parse_v3(j)
                else:
                    print('Unsupported schema : ' + schema_version)
                    print(json.dumps(json.loads(l), indent=4))
                    #sys.exit(1)

        self.print_results()

if __name__ == "__main__":
    parser = BlenderOpenDataParser()
    parser.run()