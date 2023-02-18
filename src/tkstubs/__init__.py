from .tkstubs import has_display as _has_display

HAS_DISPLAY = _has_display()

if HAS_DISPLAY:
    import tkinter as tk
    import tkinter.filedialog as tkfd
    import tkinter.messagebox as tkmb
    from tkinter import ttk
else:
    import src.tkstubs as tk

