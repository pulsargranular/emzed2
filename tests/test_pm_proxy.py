# encoding: utf-8
from __future__ import print_function


import emzed
import os


def test_0(path):
    from emzed.core.data_types.ms_types import PeakMapProxy
    pm = PeakMapProxy(path("data/SHORT_MS2_FILE.mzData"))
    # this will trigger loading:
    n = len(pm)
    assert n == 41


def test_1(path, tmpdir):
    from emzed.core.data_types.ms_types import PeakMapProxy
    pm = emzed.io.loadPeakMap(path("data/SHORT_MS2_FILE.mzData"))
    t = emzed.utils.toTable("id", (1, 2, 3), type_=int)
    t.addColumn("peakmap", pm, type_=object)
    p1 = tmpdir.join("without_comp.table").strpath
    t.store(p1 , True, True)
    p2 = tmpdir.join("with_comp.table").strpath
    t.store(p2 , True, True, tmpdir.strpath)

    # compression by peakmap proxy should be factor 30 or better in this particular case:
    s1 = os.stat(p1).st_size
    s2 = os.stat(p2).st_size
    assert s1 > 30 * s2, (s1, s2, 30 * s2)

    assert isinstance(t.peakmap.uniqueValue(), PeakMapProxy)
    assert not t.peakmap.uniqueValue()._loaded
    assert t.peakmap.uniqueValue().uniqueId() is not None    # must not trigger loading !
    assert not t.peakmap.uniqueValue()._loaded

    tn = emzed.io.loadTable(tmpdir.join("with_comp.table").strpath)
    pm = tn.peakmap.uniqueValue()
    assert t.peakmap.uniqueValue().uniqueId() is not None    # must not trigger loading !
    assert not tn.peakmap.uniqueValue()._loaded
    assert len(pm) == 41  # triggers loading
    assert tn.peakmap.uniqueValue()._loaded

    emzed.io.storeTable(t, tmpdir.join("with_comp_2.table").strpath, True, True, tmpdir.strpath)

    tn = emzed.io.loadTable(tmpdir.join("with_comp_2.table").strpath)
    pm = tn.peakmap.uniqueValue()
    assert isinstance(pm, PeakMapProxy)
    assert t.peakmap.uniqueValue().uniqueId() is not None    # must not trigger loading !
    assert not tn.peakmap.uniqueValue()._loaded
    assert len(pm) == 41  # triggers loading
    assert tn.peakmap.uniqueValue()._loaded


def test_squeeze(path):

    from emzed.core.data_types.ms_types import PeakMapProxy
    pm = PeakMapProxy(path("data/SHORT_MS2_FILE.mzData"))
    # this will trigger loading:
    n = len(pm)
    assert n == 41
    assert isinstance(pm, PeakMapProxy)
    assert "spectra" in pm.__dict__

    pm.squeeze()
    assert "spectra" not in pm.__dict__
    assert len(pm) == 41  # triggers loading
    assert "spectra" in pm.__dict__
