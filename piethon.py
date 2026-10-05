import wx
import wx.adv   
import wx.lib.scrolledpanel as scrolled
from PIL import Image, ImageFilter
from engine import PiethonEngine
import re
import os
import pygame

class AnimalPopUp(wx.Frame):
    def __init__(self, parent, path):
        super().__init__(parent, style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.NO_BORDER)
        if os.path.exists(path):
            img = wx.Image(path, wx.BITMAP_TYPE_ANY).Scale(400, 400, wx.IMAGE_QUALITY_HIGH)
            self.bmp = wx.StaticBitmap(self, -1, wx.Bitmap(img))
            self.SetSize((400, 400))
        
    def show_at(self, pos):
        self.SetPosition(pos)
        self.Show()

class CinematicOverlay(wx.Frame):
    def __init__(self, parent, gif_path, audio_path):
        super().__init__(parent, style=wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR | wx.NO_BORDER)
        self.Maximize()
        self.SetBackgroundColour(wx.BLACK)
        
        pygame.mixer.init()
        if os.path.exists(audio_path):
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()

        try:
            screen = wx.ScreenDC()
            w, h = wx.GetDisplaySize()
            bmp = wx.Bitmap(w, h)
            mem = wx.MemoryDC(bmp)
            mem.Blit(0, 0, w, h, screen, 0, 0)
            img = bmp.ConvertToImage()
            pil_img = Image.frombytes('RGB', (w, h), img.GetData()).filter(ImageFilter.GaussianBlur(radius=15))
            blur_wx = wx.Image(w, h, pil_img.tobytes())
            self.bg_bmp = wx.StaticBitmap(self, -1, blur_wx.ConvertToBitmap())
        except: pass

        if os.path.exists(gif_path):
            self.ani = wx.adv.Animation(gif_path)
            self.gif_ctrl = wx.adv.AnimationCtrl(self, -1, self.ani)
            self.gif_ctrl.SetBackgroundColour(wx.BLACK)
            self.gif_ctrl.Play()
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.AddStretchSpacer(); sizer.Add(self.gif_ctrl, 0, wx.ALIGN_CENTER); sizer.AddStretchSpacer()
            self.SetSizer(sizer)

        self.alpha = 0
        self.SetTransparent(0)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_fade, self.timer)
        self.timer.Start(15)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

    def on_fade(self, event):
        if self.alpha < 255:
            self.alpha = min(self.alpha + 5, 255)
            self.SetTransparent(self.alpha)
        else: self.timer.Stop()

    def on_key(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            pygame.mixer.music.stop()
            self.Close()
        event.Skip()

class StartMenu(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Piethon Launcher", size=(500, 300))
        self.SetBackgroundColour(wx.Colour(18, 18, 18))
        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="PIETHON CALCULATOR")
        title.SetForegroundColour(wx.Colour(255, 191, 0))
        title.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.start_btn = wx.Button(self, label="START", size=(200, 60))
        self.start_btn.Bind(wx.EVT_BUTTON, self.on_start)
        sizer.AddStretchSpacer(); sizer.Add(title, 0, wx.ALIGN_CENTER|wx.ALL, 20)
        sizer.Add(self.start_btn, 0, wx.ALIGN_CENTER|wx.BOTTOM, 40); sizer.AddStretchSpacer()
        self.SetSizer(sizer); self.Centre()

    def on_start(self, event):
        SophisticatedPieCalc().Show()
        self.Close()

class SophisticatedPieCalc(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Piethon v14.0", size=(1200, 800))
        self.is_degrees = True
        self.SetBackgroundColour(wx.Colour(18, 18, 18))
        
        self.main_layout = wx.BoxSizer(wx.HORIZONTAL)
        self.button_panel = wx.Panel(self, size=(180, -1))
        self.setup_buttons_ui()
        self.workspace = wx.Panel(self)
        self.setup_workspace_ui()
        self.history_panel = wx.Panel(self, size=(250, -1))
        self.setup_history_ui()
        
        self.main_layout.Add(self.button_panel, 0, wx.EXPAND)
        self.main_layout.Add(self.workspace, 1, wx.EXPAND)
        self.main_layout.Add(self.history_panel, 0, wx.EXPAND)
        self.SetSizer(self.main_layout); self.Centre()
        
        self.horse_popup = AnimalPopUp(self, "horse.png")

    def setup_buttons_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        funcs = [('sin', 'sin('), ('asin', 'asin('), ('cos', 'cos('), ('acos', 'acos('),
                 ('tan', 'tan('), ('atan', 'atan('), ('sqrt', 'sqrt('), ('pi', 'pi')]
        grid = wx.GridSizer(cols=2, vgap=5, hgap=5)
        for label, val in funcs:
            btn = wx.Button(self.button_panel, label=label)
            btn.Bind(wx.EVT_BUTTON, lambda e, v=val: self.input_ctrl.AppendText(v))
            grid.Add(btn, 0, wx.EXPAND)
        sizer.Add(grid, 0, wx.EXPAND|wx.ALL, 10)
        
        self.clear_btn = wx.Button(self.button_panel, label="CLEAR")
        self.clear_btn.SetBackgroundColour(wx.Colour(150, 0, 0))
        self.clear_btn.SetForegroundColour(wx.WHITE)
        self.clear_btn.Bind(wx.EVT_BUTTON, self.on_clear_all)
        
        self.mode_btn = wx.Button(self.button_panel, label="DEG")
        self.mode_btn.Bind(wx.EVT_BUTTON, self.on_toggle_mode)
        
        sizer.Add(self.clear_btn, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        sizer.Add(self.mode_btn, 1, wx.EXPAND|wx.ALL, 10)
        self.button_panel.SetSizer(sizer)

    def setup_workspace_ui(self):
        layout = wx.BoxSizer(wx.VERTICAL)
        self.horse_btn = wx.Button(self.workspace, label="", size=(30, 30))
        self.horse_btn.Bind(wx.EVT_ENTER_WINDOW, lambda e: self.horse_popup.show_at(self.ClientToScreen((100, 100))))
        self.horse_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e: self.horse_popup.Hide())

        self.input_ctrl = wx.TextCtrl(self.workspace, style=wx.TE_PROCESS_ENTER)
        self.result_lbl = wx.StaticText(self.workspace, label="Result: 0")
        self.result_lbl.SetForegroundColour(wx.Colour(255, 191, 0))
        self.result_lbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        self.visual_scroller = scrolled.ScrolledPanel(self.workspace)
        self.visual_scroller.SetupScrolling()
        self.pie_grid = wx.WrapSizer(wx.HORIZONTAL)
        self.visual_scroller.SetSizer(self.pie_grid)
        
        layout.Add(self.horse_btn, 0, wx.TOP|wx.LEFT, 10)
        layout.Add(self.input_ctrl, 0, wx.EXPAND|wx.ALL, 20)
        layout.Add(self.result_lbl, 0, wx.LEFT, 20)
        layout.Add(self.visual_scroller, 1, wx.EXPAND|wx.ALL, 10)
        self.workspace.SetSizer(layout)
        self.input_ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_calculate)

    def setup_history_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.history_list = wx.ListBox(self.history_panel)
        del_btn = wx.Button(self.history_panel, label="DELETE HISTORY")
        del_btn.Bind(wx.EVT_BUTTON, lambda e: self.history_list.Clear())
        sizer.Add(self.history_list, 1, wx.EXPAND|wx.ALL, 5); sizer.Add(del_btn, 0, wx.EXPAND|wx.ALL, 10)
        self.history_panel.SetSizer(sizer)

    def on_calculate(self, event):
        raw = self.input_ctrl.GetValue()
        if not raw: return
        calc_expr = re.sub(r'(sin|cos|tan|asin|acos|atan)\(([^)]+)\)', r'\1(radians(\2))', raw) if self.is_degrees else raw
        res, is_pi, is_67 = PiethonEngine.calculate(calc_expr)
        
        if not isinstance(res, str):
            self.result_lbl.SetLabel(f"Result: {res:.4f}")
            self.history_list.Insert(f"{raw} = {res:.4f}", 0)
            self.draw_pies(res, is_67)
            if is_67:
                CinematicOverlay(self, "KYS.gif", "audio.mp3").Show()
        self.input_ctrl.Clear()

    def draw_pies(self, val, is_67):
        self.pie_grid.Clear(True)
        img_path = "KYS.png" if is_67 else "pie.png"
        if os.path.exists(img_path):
            full_img = Image.open(img_path).convert("RGBA")
            integer_part = int(abs(val))
            decimal_part = abs(val) - integer_part
            for _ in range(min(integer_part, 200)):
                scaled = full_img.resize((80, 80), Image.Resampling.LANCZOS)
                bmp = wx.Bitmap.FromBufferRGBA(80, 80, scaled.tobytes())
                self.pie_grid.Add(wx.StaticBitmap(self.visual_scroller, -1, bmp), 0, wx.ALL, 2)
            if decimal_part > 0.01:
                d_size = int(80 * decimal_part)
                scaled_d = full_img.resize((d_size, d_size), Image.Resampling.LANCZOS)
                bmp_d = wx.Bitmap.FromBufferRGBA(d_size, d_size, scaled_d.tobytes())
                self.pie_grid.Add(wx.StaticBitmap(self.visual_scroller, -1, bmp_d), 0, wx.ALL, 2)
        self.visual_scroller.Layout(); self.visual_scroller.SetupScrolling()

    def on_toggle_mode(self, e):
        self.is_degrees = not self.is_degrees
        self.mode_btn.SetLabel("DEG" if self.is_degrees else "RAD")

    def on_clear_all(self, e):
        self.input_ctrl.Clear(); self.result_lbl.SetLabel("Result: 0"); self.pie_grid.Clear(True); self.visual_scroller.Layout()

if __name__ == "__main__":
    app = wx.App()
    StartMenu().Show(); app.MainLoop()