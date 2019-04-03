#! /usr/local/bin/python3
# coding: utf-8


# Copyright 2019 NDK
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may
# be used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import os
import sys
import re
import tempfile
import time
import platform
import subprocess

__version__ = 1.0
__author__ = "NDK"


class DiskSpeed(object):
    def __init__(self):
        self.clustersize = 64 * 1024
        self.filesize = 1000 * 1024 * 1024
        self.writefile = os.path.join(tempfile.gettempdir(), "diskspeed.tmp")
    
    def setClusterSize(self, size):
        self.clustersize = int(size) * 1024
    
    def setFileSize(self, size):
        self.filesize = int(size) * 1024 * 1024
    
    def clear(self):
        try:
            os.unlink(self.writefile)
        except FileNotFoundError:
            pass
    
    def calculateResults(self, start, end):
        diff = end - start
        speed = self.filesize / diff / 1024 / 1024
        return {
            "sec": round(diff, 2),
            "speed": round(speed, 2)
        }

    def test(self):
        print("Testing speed...")
        print(f"==> clusersize: {self.clustersize}")
        print(f"==> filesize: {self.filesize}")
        print(f'==> start time: {time.strftime("%Y-%m-%d %H:%M:%S")}')

        percent = 0

        current = 0

        start_write = time.time()
        
        fh = open(self.writefile, "wb")
        while current <= self.filesize:
            data = b"0" * self.clustersize
            fh.write(data)
            print(f"Writing: {current} of {self.filesize}...", end="\r", flush=True)
            current += self.clustersize
        fh.close()
        print("")
        
        end_write = time.time()
        
        current = 0

        start_read = time.time()
        
        fh = open(self.writefile, "rb")
        while current <= self.filesize:
            data = fh.read(self.clustersize)
            print(f"Reading: {current} of {self.filesize}...", end="\r", flush=True)
            current += self.clustersize
        fh.close()
        print("")
        
        end_read = time.time()
        
        res_read = self.calculateResults(start_read, end_read)
        res_write = self.calculateResults(start_write, end_write)

        print("=" * 50)
        print(f"Reading Time: {res_read['sec']} seconds")
        print(f"Reading Speed: ~{res_read['speed']} MB/s")
        print(f"Writing Time: {res_write['sec']} seconds")
        print(f"Writing Speed: ~{res_write['speed']} MB/s")
        print("=" * 50)

        osname = platform.system()
        if osname == "Windows":
            subprocess.call("pause", shell=True)
        elif osname == "Darwin" or osname == "Linux":
            subprocess.call('read -r -p "Press any key to continue..." key', shell=True)


if __name__ == "__main__":
    try:
        ds = DiskSpeed()
        while True:
            clustersize = input("Please give cluster size: (in KB, default 64 KB) ")
            if clustersize != "" and not re.search("^[0-9]{1,3}$", clustersize):
                continue
            if clustersize != "":
                ds.setClusterSize(clustersize)
            filesize = input("Please give temporary filesize: (in MB, default 1000 MB) ")
            if filesize != "" and not re.search("^[0-9]{1,5}$", filesize):
                continue
            if filesize != "":
                ds.setFileSize(filesize)
            break
        ds.test()
    except KeyboardInterrupt:
        print("\nProgram aborted.")
        sys.exit(0)
    except Exception as e:
        raise
    finally:
        ds.clear()
    sys.exit(0)
        