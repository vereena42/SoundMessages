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

framerate = 44100
amplitude=10000

def generate_tone(strin):
    points1 = np.round(framerate/8800)
    tone1 = (amplitude*np.sin(np.r_[0:np.pi*2:np.pi*2/points1])).astype(np.int16).tostring()
    points0 = np.round(framerate/2200)
    tone0 = (amplitude*np.sin(np.r_[0:np.pi*2:np.pi*2/points0])).astype(np.int16).tostring()
    with pa.simple.open(direction=pa.STREAM_PLAYBACK, format=pa.SAMPLE_S16LE, rate=framerate, channels=1) as player:
        t = datetime.datetime.now()
        for i in strin:
            if i=='0':
                print 0
                while (datetime.datetime.now()-t).total_seconds() < 0.5:
                    player.write(tone0)
                t+=datetime.timedelta(milliseconds=500)
            else:
                print 1
                while (datetime.datetime.now()-t).total_seconds() < 0.5:
                    player.write(tone1)
                t+=datetime.timedelta(milliseconds=500)

if __name__ == '__main__':    
    parser = argparse.ArgumentParser()
    parser.add_argument('receiver',type=int)  
    parser.add_argument('sender',type=int)
    parser.add_argument('message',nargs='*')
    args = parser.parse_args()
    rec=bin(args.receiver)
    sen=bin(args.sender)
    mess=args.message[0]
    x=32-(len(rec)-2)
    table=""
    for i in range(x):
        table=table+"0"
    table=table+rec[2:]
    x=32-(len(sen)-2)
    for i in range(x):
        table=table+"0"
    table=table+sen[2:]
    dod=4-(len(mess)%4)
    if dod==0:
        dod=4
    while dod>1:
        table+="0"
        dod-=1
    table+="1"
    table=table+mess
    crc=bin(binascii.crc32(table) & 0xffffffff)
    x=32-(len(crc)-2)
    for i in range(x):
        table=table+"0"
    table=table+crc[2:]
    fin=""
    for i in range(27):
        fin=fin+"10"
    fin=fin+"11"
    wiad=""
    y=0
    while y < len(table):
        if table[y:y+4]=="0000":
            wiad+="11110"
        elif table[y:y+4]=="0001":
            wiad+="01001"
        elif table[y:y+4]=="0010":
            wiad+="10100"
        elif table[y:y+4]=="0011":
            wiad+="10101"
        elif table[y:y+4]=="0100":
            wiad+="01010"
        elif table[y:y+4]=="0101":
            wiad+="01011"
        elif table[y:y+4]=="0110":
            wiad+="01110"
        elif table[y:y+4]=="0111":
            wiad+="01111"
        elif table[y:y+4]=="1000":
            wiad+="10010"
        elif table[y:y+4]=="1001":
            wiad+="10011"
        elif table[y:y+4]=="1010":
            wiad+="10110"
        elif table[y:y+4]=="1011":
            wiad+="10111"
        elif table[y:y+4]=="1100":
            wiad+="11010"
        elif table[y:y+4]=="1101":
            wiad+="11011"
        elif table[y:y+4]=="1110":
            wiad+="11100"
        elif table[y:y+4]=="1111":
            wiad+="11101"
        else:
            print "Error with parsing the message!"
        y=y+4
    fin=fin+wiad
    fin=fin+"0110101101"
    print "Sending:",wiad+"0110101101"
    generate_tone(fin)
    
