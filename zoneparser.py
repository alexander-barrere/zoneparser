#!/usr/bin/env python

import sys
import argparse
import dns.zone
from dns.exception import DNSException
from dns.rdataclass import *
from dns.rdatatype import *





class DnsSearch():
    def __init__(self, opts):
        self.domain = opts.domain
        self.total = 0
        if not opts.zonefile:
            self.zonefile = "db.%s" % self.domain
        else:
            self.zonefile = opts.zonefile

    def do_it(self, opts):
        zonedata = self.get_data(opts)
        if opts.nodename:
            self.search_name(zonedata, opts)
        elif opts.cname:
            self.search_cname(zonedata, opts)
        elif opts.ipv4:
            self.search_ipv4(zonedata, opts)
        elif opts.type:
            self.search_type(zonedata, opts)
        else:  # Print 'em all!
            for name, node in zonedata.nodes.items():
                rdatasets = node.rdatasets
                if opts.count: self.total +=1
		else:
                    for rdataset in rdatasets:
                        self.print_data(name, rdataset)

        if opts.count:
            print ""
            print "Here are the total occurrences: %s" % (self.total)

    def get_data(self, opts):
        try:
            zonedata = dns.zone.from_file(self.zonefile, self.domain)
            print "Zone origin:", zonedata.origin
        except DNSException, e:
            print e.__class__, e
        return zonedata

    def search_name(self, zonedata, opts):
        for name, node in zonedata.nodes.items():
            rdatasets = node.rdatasets
            if opts.nodename in name:
                if opts.count: self.total +=1
                else:
                    for rdataset in rdatasets:
                        self.print_data(name, rdataset)

    def search_cname(self, zonedata, opts):
        for name, node in zonedata.nodes.items():
            rdatasets = node.rdatasets
            for rdataset in rdatasets:
                if rdataset.rdtype == CNAME:
                    if opts.count: self.total +=1
                    else:
                        for rdata in rdataset:
                            if opts.cname in rdata.target:
                                self.print_data(name, rdataset)

    def search_ipv4(self, zonedata, opts):
        for name, node in zonedata.nodes.items():
            rdatasets = node.rdatasets
            for rdataset in rdatasets:
                if rdataset.rdtype == A:
                    if opts.count: self.total +=1
                    else:
                        for rdata in rdataset:
                            if opts.ipv4 in rdata.address:
                                self.print_data(name, rdataset)

    def search_ipv6(self, zonedata, opts):
        for name, node in zonedata.nodes.items():
            rdatasets = node.rdatasets
            for rdataset in rdatasets:
                if rdataset.rdtype == AAAA:
                    if opts.count: self.total +=1
                    else:
                        for rdata in rdataset:
                            if opts.ipv6 in rdata.address:
                                self.print_data(name, rdataset)

    def search_type(self, zonedata, opts):
        for name, node in zonedata.nodes.items():
            rdatasets = node.rdatasets
            for rdataset in rdatasets:
                if rdataset.rdtype == dns.rdatatype.from_text(opts.type):
                    if opts.count: self.total +=1
                    else:
                        for rdata in rdataset:
                            self.print_data(name, rdataset)


    def print_data(self, name, rdataset):
        print "\n**** BEGIN NODE ****"
        print "*node name:", name
        print "* --- BEGIN RDATASET ---"
        print "* rdataset string representation:", rdataset
        print "* rdataset rdclass:", rdataset.rdclass
        print "* rdataset rdtype:", rdataset.rdtype
        print "* rdataset ttl:", rdataset.ttl
        print "* rdataset has following rdata:"
        for rdata in rdataset:
            print "*     -- BEGIN RDATA --"
            print "*     rdata string representation:", rdata
            if rdataset.rdtype == SOA:
                print "*     ** SOA-specific rdata **"
                print "*     expire:", rdata.expire
                print "*     minimum:", rdata.minimum
                print "*     mname:", rdata.mname
                print "*     refresh:", rdata.refresh
                print "*     retry:", rdata.retry
                print "*     rname:", rdata.rname
                print "*     serial:", rdata.serial
            if rdataset.rdtype == MX:
                print "*     ** MX-specific rdata **"
                print "*     exchange:", rdata.exchange
                print "*     preference:", rdata.preference
            if rdataset.rdtype == NS:
                print "*     ** NS-specific rdata **"
                print "*     target:", rdata.target
            if rdataset.rdtype == CNAME:
                print "*     ** CNAME-specific rdata **"
                print "*     target:", rdata.target
            if rdataset.rdtype == A:
                print "*     ** A-specific rdata **"
                print "*     address:", rdata.address
            if rdataset.rdtype == AAAA:
                print "*    ** IPv6-specific rdata **"
                print "*     IPv6-address:", rdata.address
            print "**** END NODE ****"


#BEGIN OPTIONS
def cli_opts():
    parser = argparse.ArgumentParser(description="Search through a db.DOMAIN file.")
    parser.add_argument('--domain', action='store', dest='domain', help="Name of domain (example.com)", required=True)
    parser.add_argument('--nodename', action='store', dest='nodename', help="Search for specific node name")
    parser.add_argument('--cname', action='store', dest='cname', help="Search for specified cname")
    parser.add_argument('--type', action='store', dest='type', help="Search for specific TYPE of record (A, MX, CNAME)")
    parser.add_argument('--ipv4', action='store', dest='ipv4', help="Search for specific ipv4 address")
    parser.add_argument('--ipv6', action='store', dest='ipv6', help="Search for specific ipv6 address")
    parser.add_argument('--zonefile', action='store', dest='zonefile', help="Location of db.example.com file, else assumes in CWD")
    parser.add_argument('--count', action='store_true', help="Just return count of matches.")
    if len(sys.argv)==1:
        parser.print_help()
    return parser.parse_args()

#END OPTIONS

## Might as well start the program!

if __name__ == '__main__':
    opts = cli_opts()
    program = DnsSearch(opts)
    program.do_it(opts)
