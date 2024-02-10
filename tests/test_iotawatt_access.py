import iotawatt_access as iw


def test_time_conv_local():
    str0 = "2024-01-02T10:05:01"
    ts = iw.str_to_timestamp(str0, utc=False)
    str1 = iw.timestamp_to_str(ts, utc=False, notz=True)
    assert str0 == str1


def test_time_conv_utc():
    str0 = "2024-01-02T10:05:01"
    ts = iw.str_to_timestamp(str0, utc=True)
    str1 = iw.timestamp_to_str(ts, utc=True, notz=True)
    assert str0 == str1
