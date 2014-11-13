# /usr/bin/env python
# -*- coding:utf-8 -*-

playerurl = "http://radiko.jp/player/swf/player_3.0.0.01.swf"
playerfile = "tmp.swf"
keyfile = "tmp.png"

import urllib
import urllib2
import base64
import subprocess
import sys
import os
import argparse


class Radiko(object):

    def __init__(self, args):
        self.args = args
        self.test = self.args.verbose
        self.channel = self.args.channel
        self.areaid = self.args.areaid
        self.get_player()
        self.get_keydata()
        self.get_auth1()
        self.get_auth2()
        self.get_channels()
        self.set_channel()
        self.get_stream_url()
        self.play()

    def get_channels(self):
        self.channels = subprocess.check_output(
        "curl -s http://radiko.jp/v2/api/program/today?area_id=%s "
        % self.areaid +
        "| xmllint --format --xpath //station/@id - " +
        "| ruby -ne 'puts $_.split ' " , shell=True
        )
    
    def show_channel(self):
        print
        print self.channels
        self.channel = raw_input("select a channel: ")
        self.set_channel()
    
    def set_channel(self):
        if not self.channel:
            self.show_channel()
        if not self.channel in self.channels:
            print "station %s is not available." % self.channel
            self.show_channel()

    def get_player(self):
        '''get player'''
        body = urllib2.urlopen(playerurl).read()
        if not os.path.exists(playerfile):
            with open(playerfile, "w") as f:
                f.write(body)

    def get_keydata(self):
        '''get keydata (need swftool)'''
        if not os.path.exists(keyfile):
            cmd = "swfextract -b 14 %s -o %s" % (playerfile, keyfile)
            subprocess.call(cmd.strip().split(" "))

    def get_auth1(self):
        '''access auth1_fms'''
        auth_response = {}
        url = "https://radiko.jp/v2/api/auth1_fms"
        headers = {
            "pragma":"no-cache",
            "X-Radiko-App":"pc_1",
            "X-Radiko-App-Version":"2.0.1",
            "X-Radiko-User":"test-stream",
            "X-Radiko-Device":"pc"
        }
        values = {"\r\n:": ""}
        data = urllib.urlencode(values)

        try:
            req = urllib2.Request(url, "\r\n", headers)
            res = urllib2.urlopen(req)
            auth_response["body"] = res.read()
            auth_response["headers"] = dict(res.info())
        except:
            print "failed auth1 process"
            sys.exit()

        # get partial key

        self.authtoken  = auth_response["headers"]["x-radiko-authtoken"]
        offset = auth_response["headers"]["x-radiko-keyoffset"]
        length = auth_response["headers"]["x-radiko-keylength"]

        offset = int(offset)
        length = int(length)

        with open(keyfile, "rb+") as f:
            f.seek(offset)
            data = f.read(length)
            self.partialkey = base64.b64encode(data)

        if self.test:
            s = (self.authtoken, offset, length, self.partialkey)
            print "authtoken: %s \noffset: %s length: %s \npartialkey: %s" % s

    def get_auth2(self):
        '''access auth2_fms'''
        auth_success_responce = {}
        url = "https://radiko.jp/v2/api/auth2_fms"
        headers = {
            "pragma":"no-cache",
            "X-Radiko-App":"pc_1",
            "X-Radiko-App-Version":"2.0.1",
            "X-Radiko-User":"test-stream",
            "X-Radiko-Device":"pc",
            "X-Radiko-Authtoken":self.authtoken,
            "X-Radiko-Partialkey":self.partialkey , 
        }

        try:
            req = urllib2.Request(url, "\r\n", headers)
            res = urllib2.urlopen(req)
            auth_success_responce["body"] = res.read()
            auth_success_responce["headers"] = dict(res.info())
        except URLError, e:
            print e
            sys.exit()

        if self.test:
            print "auth_success_responce: ", auth_success_responce

        area = auth_success_responce["body"].strip().split(",")
        if not self.areaid:
            self.areaid = area[0]

        print "\narea_id:", self.areaid

    def get_stream_url(self):
        '''get stream url'''
        tmp_xml = "%s.xml" % self.channel
        if os.path.exists(tmp_xml):
            os.remove(tmp_xml)

        channel_url = "http://radiko.jp/v2/station/stream/%s.xml" \
                      % self.channel
        try:
            body = urllib2.urlopen(channel_url).read()
        except:
            print "error in to get %s" % tmp_xml
            sys.exit()
        with open(tmp_xml, 'w') as f:
            f.write(body)

        cmd = "xmllint %s.xml --xpath /url/item[1]/text() " % self.channel
        stream_url = subprocess.check_output(cmd.strip().split(" "))

        if self.test:
            print "stream_url: ", stream_url

        cmd = "echo '%s' | perl -pe 's!^(.*)://(.*?)/(.*)/(.*?)$/!$1://$2 $3 $4!'" % stream_url

        if self.test:
            print "cmd: ", cmd

        ret = subprocess.check_output(cmd, shell=True)
        self.url_parts = ret.split(" ")
        os.remove(tmp_xml)

    def play(self):
        print
        print "player start"
        options = (
            self.url_parts[0],
            self.url_parts[1],
            self.url_parts[2],
            playerurl,
            self.authtoken
        )
        play_cmd = 'rtmpdump -q -r %s --app %s --playpath %s -W %s -C S:"" -C S:"" -C S:"" -C S:%s --live' % options

        p1 = subprocess.Popen(play_cmd.strip().split(" "), stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["mplayer", "-"], stdin=p1.stdout)
        p1.stdout.close()
        try:
            output = p2.communicate()[0]
        except KeyboardInterrupt:
            print "Exit ..."

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='radiko (FM radio service in Japan) streaming application'
        )
    parser.add_argument('-a', '--areaid',
                        dest='areaid',
                        type=str,
                        default=None,
                        help='(OPTIONAL) you can choose area id (ex: "JP13")'
                        )
    parser.add_argument('-c', '--channel',
                        dest='channel',
                        type=str,
                        default=None,
                        help='(OPTIONAL) FM channel'
                        )

    parser.add_argument('-v', '--verbose',
                        help='verbose (debug) mode',
                        action='store_true'
                        )
    args = parser.parse_args()

    app = Radiko(args)

