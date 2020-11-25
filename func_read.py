#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pyasdf
import warnings
import datetime
from pyasdf import ASDFDataSet
from obspy import UTCDateTime

def read_ASDF_h5(input_files, network='*', station='*', location='*', channel='*',
                 starttime=UTCDateTime("1900-01-01T00:00:00Z"),
                 endtime=UTCDateTime("2100-01-01T00:00:00Z"),
                 tag='raw_data', auxdata=False, merge_method=1, fill_value=0, print_gaps=False,
                 automerge=False):
    """
    Reader for the converted ASDF .h5 files. Input is again a list of files. For notes on the file merging please read
    the information from read_optasense_sgy function.
    :param input_files: List of input files, best obtained from glob.glob('/path/*.h5')
    :param network: Network handle (obspy.stats.network)
    :param station: Station handle (obspy.stats.station)
    :param location: Location handle (obspy.stats.location)
    :param channel:  Channel handle (obspy.stats.channel)
    :param starttime: Read in only data from starttime to endtime
    :param endtime: Endtime of read in data
    :param tag: Default to 'raw_data'
    :param auxdata: Decide if auxiliary data should be read in. Default to True
    :param merge_method: Same as for read_optasense_sgy. Overlapping samples will be interpolated instead of masked. (
    Default to 1).
    :param fill_value: fill value for gaps in data, default to 0
    :return: combined obspy.stream object
    """
    f_it = 0
    for f in input_files:
        with pyasdf.ASDFDataSet(f, mode='r') as ds:
            tmp = ds.get_waveforms(network=network, station=station, location=location,
                                   channel=channel, starttime=starttime, endtime=endtime,
                                   tag=tag, automerge=automerge)
            if auxdata:
                attr = ds.auxiliary_data.SystemInformation.binary.parameters
                tmp.stats = attr

        if f_it == 0:
            st = tmp.copy()
        else:
            st += tmp.copy()
            if auxdata:
                if st.stats == tmp.stats:
                    pass
                else:
                    st.stats.append(tmp.stats)
            else:
                pass
        f_it += 1
    st.merge(method=merge_method, fill_value=fill_value)
    # print(st)
    #if not st.get_gaps():
    #    st.merge(method=merge_method).sort()
    #else:
    #    warnings.warn("\n"+datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S %f") +
    #                  "\n read_ASDF_h5:\n"
    #                  "Gaps or overlap in the data. Returned stream object is not merged!",
    #                  UserWarning)
    if print_gaps:
        st.print_gaps()
    return st.sort()