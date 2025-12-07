# -*- coding: utf-8 -*-
# Copyright (C) 2020-2025 by Brendt Wohlberg
# All rights reserved. GPL v2 License.

"""Classes for accessing IotaWatt status and data via the Query API."""

import os
from datetime import datetime
from json import JSONDecodeError

import numpy as np
import requests
from dateutil.parser import parse
from dateutil.tz import tzlocal, tzutc
from requests import ConnectionError
from requests.auth import HTTPDigestAuth
from requests.exceptions import RequestException

__version__ = "0.0.1.dev0"


def device_login():
    """Get device URL, username, and password.

    Return device URL, username, and password from environment variables
    "IOTAWATT_URL", "IOTAWATT_USERNAME", and "IOTAWATT_PASSWORD"
    respectively. If not set, return defaults values
    "http://iotawatt.local", "admin", and ``None`` respectively.
    """
    if "IOTAWATT_URL" in os.environ:
        url = os.environ["IOTAWATT_URL"]
    else:
        url = "http://iotawatt.local"
    if "IOTAWATT_USERNAME" in os.environ:
        user = os.environ["IOTAWATT_USERNAME"]
    else:
        user = "admin"
    if "IOTAWATT_PASSWORD" in os.environ:
        pwd = os.environ["IOTAWATT_PASSWORD"]
    else:
        pwd = None

    return url, user, pwd


def data_path():
    """Get path for data store.

    Return the data path from environment variable "IOTAWATT_DATA_PATH"
    if set. Otherwise return default value "~/IotaWatt_Data".
    """
    if "IOTAWATT_DATA_PATH" in os.environ:
        dpath = os.environ["IOTAWATT_DATA_PATH"]
    else:
        dpath = "~/IotaWatt_Data"
    return dpath


def str_to_datetime(timestr, utc=False):
    """Convert a string specifying a date and time into a datetime object.

    Args:
        timestr (str): String specifying a date and time.
        utc (bool, optional): Flag indicating whether default time zone
          should be set to UTC.

    Returns:
        datetime: A datetime object representation of the date/time.
    """
    dt = parse(timestr)
    if dt.tzinfo is None:
        if utc:
            dt = dt.replace(tzinfo=tzutc())
        else:
            dt = dt.replace(tzinfo=tzlocal())
    return dt


def str_to_timestamp(timestr, utc=False):
    """Convert a string specifying a date and time into a Unix timestamp.

    Args:
        timestr (str): String specifying a date and time.
        utc (bool, optional): Flag indicating whether default time zone
          should be set to UTC.

    Returns:
        int: Unix timestamp representation of the date/time.
    """
    return str_to_datetime(timestr, utc=utc).timestamp()


def timestamp_to_datetime(ts, utc=False):
    """Convert a Unix timestamp into a datetime object.

    Args:
        ts (int): Unix timestamp.
        utc (bool, optional): Flag indicating whether time zone should
          remain as UTC or be converted to local time.

    Returns:
        datetime: A datetime object representation of the date/time.
    """
    if utc:
        dt = datetime.fromtimestamp(ts, tz=tzutc())
    else:
        dt = datetime.fromtimestamp(ts, tz=tzlocal())
    return dt


def timestamp_to_str(ts, utc=False, notz=False):
    """Convert a Unix timestamp into an ISO-format date/time string.

    Args:
        ts (int): Unix timestamp
        utc (bool, optional): Flag indicating whether time zone should
          remain as UTC or be converted to local time.
        notz (bool, optional): Flag indicating whether the time zone
          should be included in the returned string.

    Returns:
        string: ISO format string representation of the date/time.
    """
    dt = timestamp_to_datetime(ts, utc=utc)
    if notz:
        dt = dt.replace(tzinfo=None)
    return dt.isoformat()


def _list_check(lst, rowlen):
    """Check that all rows in a nested list have the required length.

    Args:
        lst (list): List of lists.
        rowlen (int): Expected length of each inner list.

    Returns:
        ``None`` or int: ``None`` if all rows have required length,
           otherwise index of first row with incorrect length.
    """
    ret = None
    for n, row in enumerate(lst):
        if len(row) != rowlen:
            ret = n
    return ret


def _dict_get_str(d, key, fmt, cnv):
    """Get a string representation of a dictionary value.

    Args:
        d (dict): Dictionary to be accessed.
        key: Key of dict value to be retrieved.
        fmt (dict): Dictionary of string formatting specifications.
        cnv (dict): Dictionary of value mapping functions.

    Returns:
        str: String representation of retrieved dict value.
    """
    if key in d:
        v = d[key]
        if key in cnv:
            v = cnv[key](v)
        if key in fmt:
            return f"{v:{fmt[key]}}"
        else:
            return str(v)
    return ""


def dict_list_to_str(dl, keys=None, fmt=None, cnv=None):
    """Construct a tabular representation of a list of dicts.

    Args:
        dl (list): List of dicts to be tabulated.
        keys (list): List of dict keys to be tabulated.
        fmt (dict): Dictionary of string formatting specifications.
        cnv (dict): Dictionary of value mapping functions.

    Returns:
        str: Tabular representation of list of dictionaries as string.
    """
    if keys is None:
        keys = dl[0].keys()
    if fmt is None:
        fmt = {}
    if cnv is None:
        cnv = {}

    fdval = lambda d, key: _dict_get_str(d, key, fmt, cnv)

    ncol = len(keys)  # number of columns
    colw = {k: len(str(k)) for k in keys}  # column widths
    # Column width is the maximum of key width and all value widths
    for d in dl:
        colw = {k: max(len(fdval(d, k)), colw[k]) for k in keys}

    # Construct table header row
    vsep = "-" * (sum(colw.values()) + 2 * (ncol - 1)) + "\n"
    s = vsep
    s += "  ".join([k.capitalize().ljust(colw[k]) for k in keys]) + "\n"
    s += vsep

    # Construct table content
    for d in dl:
        s += "  ".join([fdval(d, k).ljust(colw[k]) for k in keys]) + "\n"
    s += vsep

    return s


def dict_to_str(d, fmt=None, cnv=None):
    """Construct a tabular representation of a dict.

    Args:
        d (dict): Dictionary to be tabulated.
        fmt (dict): Dictionary of string formatting specifications.
        cnv (dict): Dictionary of value mapping functions.

    Returns:
        str: Tabular representation of dictionary as string.
    """
    if fmt is None:
        fmt = {}
    if cnv is None:
        cnv = {}

    klen = max([len(k) for k in d.keys()])  # max key length
    vlen = max(
        [len(_dict_get_str(d, k, fmt, cnv)) for k in d.keys()]
    )  # max value length
    vsep = "-" * (klen + 2 + vlen) + "\n"  # separator bar

    s = vsep
    for k in d.keys():
        v = _dict_get_str(d, k, fmt, cnv)
        s += k.ljust(klen) + ": " + v.ljust(vlen) + "\n"

    s += vsep

    return s


class IotaWattAPI:
    """Access IotaWatt status and recorded data via the Query API.

    Attributes:
        auth (HTTPDigestAuth): Authentication for access to Query API.
        channels (list): List of IotaWatt channel names.
        inputs (list): List of IotaWatt input channel names.
        outputs (list): List of IotaWatt output channel names.
        url (str): URL for access to Query API.
    """

    def __init__(
        self,
        url="http://iotawatt.local",
        user="admin",
        pwd=None,
        debug=False,
        dbgfile="iotawatt_api_debug.log",
    ):
        """Initialize IotaWattAPI object.

        Args:
            url (str, optional): IotaWatt device URL.
            user (str, optional): IotaWatt API username.
            pwd (None, optional): IotaWatt API password.
        """
        self.url = url
        if self.url[-1] != "/":
            self.url += "/"
        if pwd is None:
            self.auth = None
        else:
            self.auth = HTTPDigestAuth(user, pwd)

        self.debug = debug
        self.dbgfile = dbgfile

        inout = self.get_channel_info()
        numout = len(self.get_status(stype="outputs"))
        self.channels = [c["name"] for c in inout]
        # Make the assumption that the voltage input is always the first
        # one in the list
        self.v_inputs = self.channels[0:1]
        self.i_inputs = self.channels[1:-numout]
        self.outputs = self.channels[-numout:]

    def get_channel_info(self, retry=3):
        """Get details of IotaWatt device input and output channels.

        Args:
            retry (int, optional): Number of retries allowed.

        Returns:
            list of dict: Channel details.
        """
        return self._query("query?show=series", retry=retry)["series"]

    def get_status(self, stype="inputs", retry=3):
        """Get IotaWatt device status.

        Valid values for stype: inputs, outputs, wifi, stats, datalogs

        Args:
            stype (str, optional): Status type.
            retry (int, optional): Number of retries allowed.

        Returns:
            dict or list of dict: Status details.
        """

        json = self._query("status?" + stype, retry=retry)
        if json:
            return json[stype]
        else:
            return []

    def get_channel_data(
        self, begin, end, channels=None, interval=5, frcdig=3, retry=3, callback=None
    ):
        """Get recorded data from IotaWatt device.

        Args:
            begin (str): Start date/time of channel data.
            end (str): End date/time of channel data.
            channels (list or ``None``, optional): List of current/power
              channel names. If ``None``, download all of them.
            interval (int, optional): Sampling interval in seconds (must
              be a multiple of 5).
            frcdig (int, optional): Number of fractional digits in
              numeric values.
            retry (int, optional): Number of retries allowed.
            callback (func or ``None``, optional): Callback function
              supporting data download progress monitoring.

        Returns:
            IotaWattData: Channel data and metadata.
        """
        if channels is None:
            channels = self.i_inputs
        datcol = (
            ["time.utc.unix"]
            + ["%s.volts.d%d" % (c, frcdig) for c in self.v_inputs]
            + ["%s.hz.d%d" % (c, frcdig) for c in self.v_inputs]
            + ["%s.watts.d%d" % (c, frcdig) for c in channels]
            + ["%s.amps.d%d" % (c, frcdig) for c in channels]
        )
        select = "[" + ",".join(datcol) + "]"

        # Estimate of row length of response to query
        rowsize = (
            14
            + len(self.v_inputs) * 2 * (7 + frcdig)
            + len(channels) * 2 * (7 + frcdig)
        )
        # Maximum response size in bytes
        maxsize = 100000
        # Maximum number of rows allowed per query
        queryrows = maxsize // rowsize

        # Begin and end dates as Unix timestamps
        tbegin = str_to_timestamp(begin)
        tend = str_to_timestamp(end)

        # Set t0 and t1 to point to start and end of time interval
        # for initial query
        t0 = tbegin
        t1 = min(tend, t0 + interval * queryrows)
        # Set number of retries for this value of t0
        t0retry = 0
        cdat = None
        # Repeat queries until start of current query interval reaches
        # end of requested interval
        while t0 < tend:
            # Call status reporting callback function if defined
            if callback is not None:
                callback(tbegin, tend, t0, t1)
            # Construct query and get response
            query = (
                "select=%s&begin=%10d&end=%10d&group=%ds&format=json&" "missing=skip"
            ) % (select, t0, t1, interval)
            json = self._query("query?" + query, retry=retry)
            if len(json) == 0:
                # If the request does not result in any errors but has
                # zero length, assume that the corresponding data is
                # missing from the device history
                t0 = t1
                t1 = min(tend, t0 + interval * queryrows)
                continue
            # Check JSON response list for rows with incorrect length
            # (not clear why these are encountered occasionally)
            rowidx = _list_check(json, len(datcol))
            if rowidx is None:
                # No row length errors
                cblk = np.array(json)
                t0 = t1
                t0retry = 0
            else:
                # Row length error encountered
                RuntimeWarning("Bad record received for time %d" % json[rowidx][0])
                if rowidx > 0:
                    # Row length error is not in first row: assume that
                    # the preceding rows are valid and prepare to retry
                    # starting at the problematic row
                    cblk = np.array(json[0 : rowidx - 1])
                    t0 = json[rowidx][0]
                    t0retry = 0
                else:
                    # Row length error in in the first row: discard the
                    # entire list of rows and prepare to retry with the
                    # same starting time as the previous query
                    cblk = None
                    t0retry += 1
            if cblk is None:
                # Allow only a limited number of retries with the same
                # value of t0
                if t0retry > 2:
                    raise RuntimeError(
                        "Too many failures in accessing"
                        " data block starting at time %d" % t0
                    )
            else:
                # Set or extend the array accumulating the full set of
                # rows obtained over multiple requests
                if cdat is None:
                    cdat = cblk
                else:
                    cdat = np.vstack((cdat, cblk))
                # Update end of query interval
                t1 = min(tend, t0 + interval * queryrows)

        return IotaWattData(
            begin, end, self.v_inputs, channels, frcdig, cols=datcol[1:], data=cdat
        )

    def _query(self, query, retry=3):
        """Send query via device API and get response.

        Args:
            query (str): Query string.
            retry (int, optional): Number of retries allowed.

        Returns:
            dict: JSON formatted response.

        Raises:
            ConnectionError: Error in connecting to device.
            RuntimeError: Maxumum retries exceeded, or error in parsing
                device response.
        """
        req = self.url + query
        if self.debug:
            self._debug_write("REQUEST\n%s\n" % req)

        response = None
        for reqtry in range(retry):
            jsonfail = False
            try:
                response = requests.get(req, auth=self.auth)
            except RequestException as ex:
                RuntimeWarning(ex)
                continue
            if self.debug:
                self._debug_write("STATUS CODE: %d\n" % response.status_code)
            if response.status_code == 200:
                if self.debug:
                    self._debug_write("RESPONSE\n%s\n" % response.text)
                try:
                    json = response.json()
                except JSONDecodeError:
                    jsonfail = True
                    RuntimeWarning("JSON parse error")
                    if self.debug:
                        self._debug_write("JSON PARSE ERROR\n")
                else:
                    if self.debug:
                        self._debug_write("JSON PARSE SUCCESS\n")
                    break
            else:
                RuntimeWarning("Connection error code %d" % response.status_code)

        if reqtry >= retry:
            raise RuntimeError(
                "Maximum number of retries exceeded (%d tries)" % (reqtry + 1)
            )
        if response is None:
            raise RuntimeError("Unrecognized failure")
        if response.status_code != 200:
            raise ConnectionError("Connection error code %d" % response.status_code)
        if jsonfail:
            raise RuntimeError(
                "Error parsing JSON response (length %d) to "
                "query %s" % (len(response.text), query)
            )

        if self.debug:
            self._debug_write("JSON\n%s\n\n" % json)

        return json

    def _debug_write(self, text):
        """Write a transaction log for debugging purposes.

        Args:
            text (str): Text to add to transaction log.
        """
        f = open(self.dbgfile, "a+")
        f.write(text)
        f.close()


class IotaWattData:
    """Dataset downloaded from IotaWatt device.

    Attributes:
        begin (str): Start date/time of channel data.
        vchannels (list): List of voltage channel names.
        ichannels (list): List of current/power channel names.
        data (numpy array): Array of channel data.
        end (str): End date/time of channel data.
        frcdig (int): Number of fractional digits in numeric values.
        time (numpy array): Array of sample times as Unix timestamps.
        units (str): Units for channel data.
    """

    def __init__(
        self, begin, end, vchannels, ichannels, frcdig, cols=None, data=None, time=None
    ):
        """Initialize IotaWattData object.

        Args:
            begin (str): Start date/time of channel data.
            end (str): End date/time of channel data.
            vchannels (list): List of voltage channel names.
            ichannels (list): List of current/power channel names.
            frcdig (int): Number of fractional digits in numeric values.
            cols (list or ``None``, optional): List of data column
              descriptions.
            data (numpy array or ``None``, optional): Array of channel
              data.
            time (numpy array or ``None``, optional): Array of sample
              times.
        """
        self.begin = begin
        self.end = end
        self.vchannels = vchannels
        self.ichannels = ichannels
        self.frcdig = frcdig
        self.cols = cols
        if time is None and data is not None:
            self.time = data[:, 0].astype(int)
            self.data = data[:, 1:].astype(np.float32)
        else:
            self.time = time
            self.data = data

    def get_channel_data(self, name, units):
        """Get data from channel `name` in units `units`.

        Args:
            name (str): Channel name.
            units (str): Data units. Valid values are 'volts' and 'hertz'
              for voltage channels and 'watts', 'amps', 'wh', 'va', 'var',
              'varh', 'pf' for current/power channels.

        Returns:
            numpy array: Channel data.
        """
        if name not in self.vchannels and name not in self.ichannels:
            raise ValueError("No data for channel %s" % name)
        if name in self.vchannels:
            # Voltage channel selected
            if units not in ["volts", "hertz"]:
                raise ValueError("Unrecognized units %s" % units)
            if units == "volts":
                c = self.data[:, 0]
            else:
                c = self.data[:, 1]
        else:
            # Current/power channel selected
            if units not in ["watts", "amps", "wh", "va", "var", "varh", "pf"]:
                raise ValueError("Unrecognized units %s" % units)
            idx = self.ichannels.index(name)
            v = self.data[:, 0]
            w = self.data[:, idx + 2]
            a = self.data[:, idx + len(self.ichannels) + 2]
            if units == "watts":
                c = w
            elif units == "amps":
                c = a
            elif units == "wh":
                c = w * (5.0 / 3600.0)
            elif units == "va":
                c = v * a
            elif units == "var":
                c = np.sqrt((v * a) ** 2 - w**2)
            elif units == "varh":
                vah = v * a * (5.0 / 3600.0)
                wh = w * (5.0 / 3600.0)
                c = np.sqrt(vah**2 - wh**2)
            else:  # units == 'pf'
                c = w / (v * a)
        return c

    def save(self, filename):
        """Save data in numpy NPZ format.

        Args:
            filename (str): Filename.
        """
        np.savez(
            filename,
            time=self.time,
            data=self.data,
            cols=self.cols,
            begin=self.begin,
            end=self.end,
            vchannels=self.vchannels,
            ichannels=self.ichannels,
            frcdig=self.frcdig,
        )

    @classmethod
    def load(cls, filename):
        """Load data from numpy NPZ format file.

        Args:
            filename (str): Filename.

        Returns:
            IotaWattData : Object data retrieved from file.
        """
        npz = np.load(filename)
        return cls(
            npz["begin"].item(),
            npz["end"].item(),
            list(npz["vchannels"]),
            list(npz["ichannels"]),
            npz["frcdig"],
            list(npz["cols"]),
            npz["data"],
            npz["time"],
        )
