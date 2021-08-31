import pynvim
import pynvim.api.buffer as nvimbuf
import pynvim.api.window as nvimin

from sys import platform

IS_MAC = False
if platform == 'darwin':
    from AppKit import NSPasteboard, NSPasteboardTypeString
    IS_MAC = True
else:
    import pyperclip

@pynvim.plugin
class NClip:
    def __init__(self, nvim):
        self.nvim = nvim
        if IS_MAC:
            self.pb = NSPasteboard.generalPasteboard()
        else:
            self.pb = None
        self.buf = None

    def prepBuf(self):
        self.buf = self.nvim.api.create_buf(False, True) # as a scratch buf
        self.nvim.api.buf_set_option(self.buf, "filetype", "NClipboard")
        return self.buf
        

    @pynvim.command(name="NClip")
    def entrance(self):
        ui = self.nvim.api.list_uis()[0]
        height = (ui['height'] * 8) // 10
        width = (ui['width'] * 8) // 10
        opts = {
            'relative': 'editor',
            'width': width,
            'height': height,
            'col': (ui['width']//2) - (width//2),
            'row': (ui['height']//2) - (height//2),
            'anchor': 'NW',
            'style': 'minimal',
            'border': "shadow"
        }
        buf = self.prepBuf()
        self.nvim.api.open_win(buf, True, opts)

    @pynvim.command(name="NClipSession")
    def nclipOnly(self):
        buf = self.prepBuf()
        self.nvim.api.set_current_buf(buf)

    @pynvim.command(name="NClipS")
    def splits(self):
        self.nvim.command("bo split")
        buf = self.prepBuf()
        win = self.nvim.current.window
        self.nvim.api.win_set_buf(win, buf)

    @pynvim.command(name="NClipV")
    def splitv(self):
        self.nvim.command("bo vsplit")
        buf = self.prepBuf()
        win = self.nvim.current.window
        self.nvim.api.win_set_buf(win, buf)

    @pynvim.command(name="NClipWrite")
    def write(self):
        buf = self.buf or self.nvim.current.buffer
        self._setCB(buf)

    @pynvim.command(name="NClipRead")
    def load(self):
        self._setBuf(self.nvim.current.buffer)

    @pynvim.autocmd('FileType', pattern="NClipboard", allow_nested=True, sync=True)
    def set_buf(self):
        self._setBuf(self.nvim.current.buffer)
        self.nvim.command("autocmd TextChanged,TextChangedI,CmdwinEnter <buffer> :NClipWrite")

    def _setBuf(self, buf):
        content = getFromCB(self.pb)
        buf[:] = content.split("\n")

    def _setCB(self, buf):
        content = '\n'.join(buf[:])
        setToCB(self.pb, content)

def getFromCB(pb):
    if IS_MAC:
        return pb.stringForType_(NSPasteboardTypeString)
    else:
        return pyperclip.paste()

def setToCB(pb, content):
    if IS_MAC:
        pb.prepareForNewContentsWithOptions_(1)
        pb.setString_forType_(content, NSPasteboardTypeString)
    else:
        pyperclip.copy(content)
