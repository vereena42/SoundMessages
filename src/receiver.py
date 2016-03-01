#!/usr/bin/env python2
# vim:ts=4:sts=4:sw=4:expandtab

# Copyright (c) 2015, Dominika Salawa <vereena42@gmail.com>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
# 
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
# 
#     * Neither the name of the <organization> nor the names of its
#       contributors may be used to endorse or promote products derived from this
#       software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import numpy as np

import pulseaudio as pa

import argparse

import datetime

import binascii

import timer

framerate = 44100
amplitude=10000
t = None

def find_tone(time):
    global t
    hertz=[]
    arr=[]
    with pa.simple.open(direction=pa.STREAM_RECORD, format=pa.SAMPLE_S16LE,
            rate=framerate, channels=1) as recorder:
        arr = recorder.read(11264)
        while (datetime.datetime.now()-t).total_seconds() < time/2:
            arr = recorder.read(11264)
        arr = [arr[i*512:(i+1)*512] for i in range(len(arr) // 512)]
    for data in arr:
        data = np.fromstring(data,np.int16)
        data = np.fft.fft(data)
        freqs = np.fft.fftfreq(len(data))
        data = np.abs(data).astype(int)
        ind = np.argmax(np.abs(data).astype(int))
        freq = freqs[ind]
        her = abs(freq * framerate)
        hertz.append(her)
    t+=datetime.timedelta(seconds=time)
    while datetime.datetime.now() < t:
        pass
    if max(hertz)-min(hertz)>8000:
        return 0.
    return sum(hertz)/len(hertz)

def receive():
    global t
    table=""
    flag = 1
    was_receiving = 0
    is_ok = 0
    y=0.25
    t = datetime.datetime.now()
    if True:
        while flag==1:
            x = find_tone(0.496)
            if is_ok==0:
                if x<1800 or x>9000:
                    pass
                else:
                    was_receiving = 1
                    if 2050 < x < 2350:
                        is_ok = 1
                    elif 8650 < x < 8950:
                        is_ok = 1
                    else:
                         t+=datetime.timedelta(seconds=y)
                         while datetime.datetime.now() < t:
                             pass
                         y=y/2
            else:
                if x<(1/1.1)*2200 or x>1.1*8800:
                    flag = 0
                elif (1/1.1)*2200 <= x < 1.1*2200:
                        table=table+"0"
                        print 0,
                elif (1/1.1)*8800 <= x < 1.1*8800:
                        table=table+"1"
                        print 1,
                elif 1.1*2200 <= x < 5500:
                        table=table+"0"
                        t+=datetime.timedelta(seconds=0.08)
                        while datetime.datetime.now() < t:
                             pass
                        print "::: moving forward :::"
                        print 0,
                elif 5500 <= x < (1/1.1)*8800:
                        table=table+"1"
                        t+=datetime.timedelta(seconds=0.08)
                        while datetime.datetime.now() < t:
                             pass
                        print "::: moving forward :::"
                        print 1,
            print x
    y=1
    previous=table[0]
    while y<len(table):
        if table[y]==previous:
            table=table[y+1:]
            break
        previous=table[y]
        y=y+1
    print "Received:",table
    if table[len(table)-10:]!="0110101101":
        print "Error! End of message not found."
    y=0
    table=table[:len(table)-10]
    wiad=""
    while y < len(table):
        if table[y:y+5]=="11110":
            wiad+="0000"
        elif table[y:y+5]=="01001":
            wiad+="0001"
        elif table[y:y+5]=="10100":
            wiad+="0010"
        elif table[y:y+5]=="10101":
            wiad+="0011"
        elif table[y:y+5]=="01010":
            wiad+="0100"
        elif table[y:y+5]=="01011":
            wiad+="0101"
        elif table[y:y+5]=="01110":
            wiad+="0110"
        elif table[y:y+5]=="01111":
            wiad+="0111"
        elif table[y:y+5]=="10010":
            wiad+="1000"
        elif table[y:y+5]=="10011":
            wiad+="1001"
        elif table[y:y+5]=="10110":
            wiad+="1010"
        elif table[y:y+5]=="10111":
            wiad+="1011"
        elif table[y:y+5]=="11010":
            wiad+="1100"
        elif table[y:y+5]=="11011":
            wiad+="1101"
        elif table[y:y+5]=="11100":
            wiad+="1110"
        elif table[y:y+5]=="11101":
            wiad+="1111"
        else:
            print "Error with receiving! Wrong message lenght."
        y=y+5
    y=0;
    rec=int(wiad[y:y+32],2)
    print "Receiver:",rec
    y+=32
    sen=int(wiad[y:y+32],2)
    print "Sender:",sen
    y+=32
    crc_table=""
    crc=bin(binascii.crc32(wiad[:len(wiad)-32]) & 0xffffffff)
    x=32-(len(crc)-2)
    for i in range(x):
        crc_table=crc_table+"0"
    crc_table=crc_table+crc[2:]
    while wiad[y]=="0":
        y+=1
    y+=1
    print "Message:",wiad[y:len(wiad)-32]
    if crc_table!=wiad[len(wiad)-32:]:
        print "Error! Checksum is not right!"
    else:
        print "Checksum is ok." 

if __name__ == '__main__':
    receive()
