import guidata
app = guidata.qapplication()

import emzed



t = emzed.utils.toTable("rt", (10.0, 20.0))
emzed.gui.inspect(t)

t = emzed.utils.toTable("rt", (10.0, 20.0), meta=dict(time_is_in_seconds=False))
emzed.gui.inspect(t)
