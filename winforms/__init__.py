from . import controls
from .forms import Form

from clr import System


# TODO: As applications become more complex, we might have ppl start calling these items themselves.
#   If that needs to be done, break them off into simlar methods here.
System.Windows.Forms.Application.EnableVisualStyles()
System.Windows.Forms.Application.SetCompatibleTextRenderingDefault(False)


def run(form_output):
    return System.Windows.Forms.Application.Run(form_output)
