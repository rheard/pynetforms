from . import controls
from .forms import Form

from clr import System


def run(form_output):
    return System.Windows.Forms.Application.Run(form_output)
