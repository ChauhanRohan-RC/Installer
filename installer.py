import os
import sys
from tkinter import Tk, Label, Frame, Entry, filedialog, messagebox
from tkinter.ttk import Progressbar
from tkwidgets import HoverB
from zipfile import ZipFile
import pickle
import shutil
from threading import Thread
from subprocess import Popen, STARTUPINFO, STARTF_USESHOWWINDOW
import ctypes
import winreg
import winfonts


# .........................    Static Functions    ...................................

def rgb(*args):
    return '#%02x%02x%02x' % args


def is_admin():
    """ returns 1 if admin ,0 otherwise"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return 0


def run_as_admin(executable, arg=None):
    ctypes.windll.shell32.ShellExecuteW(None, 'runas', executable, arg, None, 1)


def get_reg_value(field, key_path, name):
    """
    :param field: winreg cons
    :param key_path: path to key
    :param name: caption of value
    :return: (value data, type_id) if key exists, else None, None
    """
    try:
        with winreg.OpenKey(field, key_path) as key:
            return winreg.QueryValueEx(key, name)

    except (OSError, PermissionError, Exception):
        return None, None


def set_permissions(_dir):
    """
    :param _dir: directory t give full control to user
    """
    _user_name = os.getenv('username')
    _per_bat_path = os.path.join(main_dir, 'permissions.bat')
    with open(_per_bat_path, 'w+') as bfile:
        bfile.write(f'icacls "{_dir}" /grant "{_user_name}":(OI)(CI)F /T')

    s_info = None
    if os.name == 'nt':
        s_info = STARTUPINFO()
        s_info.dwFlags |= STARTF_USESHOWWINDOW

    _per_p = Popen([_per_bat_path], startupinfo=s_info)
    _per_p.wait()


def get_setup_info(file_path):
    """
    :param file_path: path of info.cc in form  {'zip_name' : 'main.zip',
                                                'exe_in_zip': ['reg.exe', 'as.exe', ],
                                                'soft_name': 'Twilight',
                                                'version': '7.9.8',
                                                'soft_author': 'Rc',
                                                'soft_des': 'description',
                                                'uninstall_key_name': 'Twilight',  in windows registry
                                                'main_exe_name': 'Twilight'}   main exe to cross check installation
                                                'permissions' : 'no'}   'no' or 'yes' (to allow read and write permissions in install dir)

            zip should not contain root directory, it will be created automatically
    :return: info dic or None in case of error
    """
    if os.path.isfile(file_path):
        try:
            with open(file_path, 'rb') as _f:
                info_ = pickle.load(_f)
        except Exception as e:
            print(e)
            return None
        else:
            return info_
    else:
        return None


# .........................................    Global settings    ..................
frozen = getattr(sys, 'frozen', False)
main_dir = os.path.dirname(sys.executable) if frozen else os.path.dirname(
            os.path.abspath(os.path.realpath(__file__)))

sdk_dir = os.path.join(main_dir, "sdk")
src_dir = os.path.join(sdk_dir, "src")
fonts_dir = os.path.join(sdk_dir, "fonts")
icons_dir = os.path.join(sdk_dir, "icons")

# icon
window_icon = os.path.join(icons_dir, 'install.ico')
ext_fonts = [
    # "product_sans_light.ttf",
    # "product_sans_medium.ttf",
    "product_sans_regular.ttf",
    # "product_sans_thin.ttf"
]

# color scheme
bg = rgb(10, 10, 10)
fg = rgb(250, 250, 250)
abg = rgb(40, 40, 40)
afg = rgb(32, 218, 255)

# fonts
b_font = ('product sans', 9)
main_l_font = ('product sans', 18)
sub_l_font = ('product sans', 9)
finish_l_font = ('product sans', 16)
e_font = ('product sans', 8)
e_insertbg = rgb(240, 240, 240)     # cursor color

# buttons style
b_relief = 'flat'
b_bd = 0

# entry_style
e_relief = 'groove'
e_bd = 4


# ...........................       Sub Classes         ...........................
class InfoFrame(Frame):
    """
    contains all attrs related to setup info
    """

    def __init__(self, master, setup_info):
        self.master = master
        self.setup_info = setup_info

        # loading setup info
        self.zip_name = self.setup_info['zip_name']
        self.exe_in_zip = self.setup_info['exe_in_zip']
        self.soft_name = self.setup_info['soft_name']
        self.soft_ver = self.setup_info['version']
        self.soft_author = self.setup_info['soft_author']
        self.soft_des = self.setup_info['soft_des']
        self.main_exe_name = self.setup_info['main_exe_name']
        self.uninstall_key_name = self.setup_info['uninstall_key_name']
        if 'permissions' in self.setup_info:
            self.permissions = self.setup_info['permissions']
        else:
            self.permissions = 'yes'

        # main zip info
        self.zip_path = os.path.join(src_dir, self.zip_name)
        try:
            self.zip = ZipFile(self.zip_path, 'r')
        except Exception:
            exit_on_error("Fatal Error", "Failed to parse source files")
        self.zip_info = self.zip.infolist()
        self.zip_uncom_size = sum((_f.file_size for _f in self.zip_info))  # in bytes

        Frame.__init__(self, self.master, bg=bg)
        self.name_l = Label(self, bg=bg, fg=fg, font=main_l_font,
                            text='%s v%s' % (self.soft_name, self.soft_ver), anchor='n')
        self.author_l = Label(self, bg=bg, fg=fg, font=sub_l_font,
                              text='Author: %s' % self.soft_author, anchor='w')
        self.des_l = Label(self, bg=bg, fg=fg, font=sub_l_font,
                           text='Description: %s' % self.soft_des, anchor='w')
        self.space_l = Label(self, bg=bg, fg=fg, font=sub_l_font,
                             text='Space Required: %d MiB' % round((self.zip_uncom_size / (1024 ** 2)), 2),
                             anchor='w')

        self.name_l.pack(fill='x', padx=10, pady=30, anchor='n')
        self.author_l.pack(fill='x', padx=20, pady=3, anchor='w')
        self.des_l.pack(fill='x', padx=20, pady=3, anchor='w')
        self.space_l.pack(fill='x', padx=20, pady=3, anchor='w')


class UserInput(Frame):
    def __init__(self, master, next_call, cancel_call):
        self.master = master
        self.next_call = next_call
        self.cancel_call = cancel_call

        Frame.__init__(self, self.master, bg=bg)
        self.entry_f = Frame(self, bg=bg)
        self.dir_e = Entry(self.entry_f, font=e_font, relief=e_relief, bd=e_bd, bg=bg, fg=fg, insertbackground=e_insertbg)
        self.dir_e.insert('end', os.getenv('ProgramFiles'))
        self.browse_b = HoverB(self.entry_f, text='Browse', fg=fg, bg=bg, activebackground=abg,
                               activeforeground=afg, hoverbg=abg, hoverfg=afg, command=self.browse_call, relief='flat', bd=0,
                               font=e_font, width=8)
        self.browse_b.pack(side='right', padx=4)
        self.dir_e.pack(side='right', fill='x', expand=True)

        self.prev_next_f = Frame(self, bg=bg)
        self.next_b = HoverB(self.prev_next_f, text='Next', fg=fg, bg=bg, activebackground=abg,
                             activeforeground=afg, hoverbg=abg, hoverfg=afg, command=self.next_call, relief='flat', bd=0, font=b_font,
                             width=6)
        self.cancel_b = HoverB(self.prev_next_f, text='Cancel', fg=fg, bg=bg, activebackground=abg,
                               activeforeground=afg, hoverbg=abg, hoverfg=afg, command=self.cancel_call, relief='flat', bd=0,
                               font=b_font, width=8)
        self.next_b.pack(side='right', padx=4)
        self.cancel_b.pack(side='right')

        self.entry_f.pack(fill='x', expand=True, padx=12, pady=6)
        self.prev_next_f.pack(anchor='e', padx=2, pady=6)

        # self.dir_e.place(x=15, relwidth=.8, y=10)
        # self.browse_b.place(relx=.85, y=10)
        # self.next_b.place(relx=.97, rely=.95, anchor='se')
        # self.cancel_b.place(relx=.86, rely=.95, anchor='se')

    def browse_call(self, event=None):
        __in = filedialog.askdirectory(initialdir='C;//', title='Select Installation Directory')
        if __in:
            self.dir_e.delete(0, 'end')
            self.dir_e.insert('end', __in)


class InstallCheck(Frame):
    def __init__(self, master, soft_name, uninstall_key, main_exe_name, uninstall_call, cancel_call):
        self.master = master
        self.un_key = uninstall_key
        self.main_exe_name = main_exe_name
        self.soft_name = soft_name
        self.uninstall_call = uninstall_call
        self.cancel_call = cancel_call

        self.uninstall_exe_path = get_reg_value(winreg.HKEY_LOCAL_MACHINE, f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.un_key}", "UninstallString")[0]
        _prev_v = get_reg_value(winreg.HKEY_LOCAL_MACHINE, f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.un_key}", "DisplayVersion")[0]
        self.previous_ver = _prev_v if _prev_v else ''

        Frame.__init__(self, master, bg=bg)

        self.l_frame = Frame(self, bg=bg)
        self.label1 = Label(self.l_frame, bg=bg, fg=fg, text=f'{self.soft_name} {self.previous_ver} already installed', font=finish_l_font, anchor='center')
        self.label2 = Label(self.l_frame, bg=bg, fg=fg, text='Do you want to uninstall Previous Version and continue setup?', font=sub_l_font, anchor='center')
        self.label1.pack(fill='x')
        self.label2.pack(fill='x')

        self.b_frame = Frame(self, bg=bg)
        self.un_b = HoverB(self.b_frame, text='Uninstall', fg=fg, bg=bg, activebackground=abg, activeforeground=afg, hoverbg=abg, hoverfg=afg,
                           command=self.uninstall_call, relief='flat', bd=0, font=b_font, width=10)
        self.cancel_b = HoverB(self.b_frame, text='Cancel', fg=fg, bg=bg, activebackground=abg,
                               activeforeground=afg, hoverbg=abg, hoverfg=afg, command=self.cancel_call,
                               relief='flat', bd=0, font=b_font, width=8)
        self.un_b.pack(side="right", padx=4)
        self.cancel_b.pack(side="right")

        self.l_frame.place(anchor='center', relx=0.5, rely=0.5)
        self.b_frame.place(anchor='se', relx=0.99, rely=0.98)

        # self.label1.place(relx=0.5, rely=0.35, anchor='center', relwidth=1)
        # self.label2.place(relx=0.5, rely=0.6, anchor='center', relwidth=1)

    @property
    def is_installed(self):
        if self.uninstall_exe_path and os.path.isfile(self.uninstall_exe_path) and os.path.isfile(os.path.join(os.path.dirname(self.uninstall_exe_path), self.main_exe_name + '.exe')):
            return True
        return False


class MainFrame(Frame):
    """
    info_f attribute is a Frame having all info about setup and zip
    """

    def __init__(self, master, setup_info, next_call, cancel_call):
        Frame.__init__(self, master, bg=bg)
        self.info_f = InfoFrame(self, setup_info=setup_info)
        self.input_f = UserInput(self, next_call=next_call, cancel_call=cancel_call)

        self.input_f.pack(fill='x', side="bottom", pady=2, expand=True)
        self.info_f.pack(fill='both', side="bottom", pady=6, expand=True)


class InstallFrame(Frame):
    def __init__(self, master, width, cancel_call):
        self.master = master
        self.width = width
        self.cancel_call = cancel_call

        Frame.__init__(self, self.master, bg=bg)
        self.prog_f = Frame(self, bg=bg)
        self.prog_l = Label(self.prog_f, bg=bg, fg=fg, text='Installing  0.0%', font=sub_l_font)
        self.prog_bar = Progressbar(self.prog_f,  mode='determinate', orient='horizontal', length=self.width - 40,
                                    maximum=100, value=0)

        self.prog_l.pack(padx=20, pady=3)
        self.prog_bar.pack(fill='x', expand=True, padx=20)

        self.cancel_b = HoverB(self, text='Cancel', fg=fg, bg=bg, activebackground=abg,
                               activeforeground=afg, hoverbg=abg, hoverfg=afg, command=self.cancel_call, relief='flat', bd=0,
                               font=b_font, width=8)

        self.prog_f.place(anchor='center', relx=0.5, rely=0.45)
        self.cancel_b.place(relx=.99, rely=.95, anchor='se')


class FinishFrame(Frame):
    def __init__(self, master, finish_call=None, message='Setup completed successfully'):
        self.master = master
        self.finish_call = finish_call if finish_call else self.end
        self.message = message

        Frame.__init__(self, master, bg=bg)
        self.label = Label(self, bg=bg, fg=fg, text=self.message, font=finish_l_font, anchor='center')
        self.finish_b = HoverB(self, text='Finish', fg=fg, bg=bg, activebackground=abg,
                               activeforeground=afg, hoverbg=abg, hoverfg=afg, command=self.finish_call, relief='flat', bd=0, font=b_font)

        self.label.place(relx=0.5, rely=0.5, anchor='center', relwidth=1)
        self.finish_b.place(relx=0.99, rely=0.98, anchor='se')

    def end(self):
        self.master.destroy()
        sys.exit()


class FailedFrame(Frame):
    def __init__(self, master, finish_call=None, message='Setup Failed', error_code=''):
        self.master = master
        self.finish_call = finish_call if finish_call else self.end
        self.message = message
        self.error_code = error_code

        Frame.__init__(self, master, bg=bg)
        self.l_frame = Frame(self, bg=bg)
        self.fail_l = Label(self.l_frame, bg=bg, fg=fg, text=self.message, font=finish_l_font, anchor='center')
        self.error_l = Label(self.l_frame, bg=bg, fg=fg, font=sub_l_font, anchor='center')
        self.set_error(error_code)

        self.fail_l.pack()
        self.error_l.pack()

        self.finish_b = HoverB(self, text='Finish', fg=fg, bg=bg, activebackground=abg,
                               activeforeground=afg, hoverbg=abg, hoverfg=afg,
                               command=self.finish_call, relief='flat', bd=0, font=b_font, width=8)

        self.l_frame.place(relx=0.5, rely=0.5, anchor='center')
        self.finish_b.place(relx=0.99, rely=0.98, anchor='se')

    def end(self):
        self.master.destroy()
        sys.exit()

    def set_error(self, error):
        self.error_l.configure(text=f'Error Code: {error}')


# ...........................        Main Installer Tk class        .............................
class Installer(Tk):
    def __init__(self, setup_info, width=550, height=310):
        self.setup_info = setup_info
        self.width, self.height = width, height

        # main logic
        self.in_dir = None
        self.extraction_paused = False

        Tk.__init__(self)
        self.s_width, self.s_height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.x, self.y = round((self.s_width - self.width) / 2), round((self.s_height - self.height) / 2)
        self.geometry(f'{self.width}x{self.height}+{self.x}+{self.y}')
        self.resizable(0, 0)
        if os.path.exists(window_icon):
            self.iconbitmap(window_icon)
        self['bg'] = bg

        # Frames
        self.main_f = MainFrame(self, setup_info, self.main_f_next, self.main_f_cancel)
        self.unins_f = InstallCheck(self, self.main_f.info_f.soft_name, self.main_f.info_f.uninstall_key_name, self.main_f.info_f.main_exe_name, self.uninstall_call, self.main_f_cancel)
        self.install_f = InstallFrame(self, self.width, self.install_f_cancel)
        self.finish_f = FinishFrame(self)
        self.fail_f = FailedFrame(self, message='Setup Failed')

        self.protocol('WM_DELETE_WINDOW', self.main_f_cancel)  # need to be set in every step
        self.title('%s %s Setup' % (self.main_f.info_f.soft_name, self.main_f.info_f.soft_ver))  # set after main_f

        self.check_prev_install()

    def check_prev_install(self):
        if self.unins_f.is_installed:
            self.unins_f.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.main_f.place(x=0, y=0, relwidth=1, relheight=1)
            self.main_f.input_f.focus_set()

    def uninstall_call(self):
        if self.unins_f.is_installed:
            _unins_call = Popen([self.unins_f.uninstall_exe_path, '-force'])
            _unins_call.wait()

        self.unins_f.place_forget()
        self.main_f.place(x=0, y=0, relwidth=1, relheight=1)
        self.main_f.lift()
        self.main_f.input_f.focus_set()

    def main_f_next(self):
        __temp = self.main_f.input_f.dir_e.get()
        if __temp:
            if os.path.isdir(__temp):
                self.in_dir = __temp
            else:
                try:
                    os.makedirs(__temp)
                except Exception as e:
                    print(e)
                    messagebox.showerror(parent=self, title='Invalid Input',
                                         message=f'Unable to create input directory \n\nError Code : {e} ')
                    self.in_dir = None
                else:
                    self.in_dir = __temp
            if self.in_dir:
                self.main_f.place_forget()
                self.extract_ui(self.in_dir)

    def main_f_cancel(self, event=None):
        """ cancel on main frame """
        __in = messagebox.askyesno('Confirm Exit', 'Are you Sure to cancel the setup', parent=self)
        if __in:
            self.main_f.place_forget()
            self.fail_ui('Cancelled by user')

    def _extract(self, out_dir):
        main_out_dir = os.path.join(out_dir, '%s %s' % (self.main_f.info_f.soft_name, self.main_f.info_f.soft_ver))
        _cancel = False  # for cancelling extraction progress in between
        try:
            if not os.path.isdir(main_out_dir):
                os.makedirs(main_out_dir)
            _per = 0.00
            for _file in self.main_f.info_f.zip_info:
                self.main_f.info_f.zip.extract(_file, main_out_dir)
                _per += round((_file.file_size / self.main_f.info_f.zip_uncom_size) * 100, 2)
                self.install_f.prog_l['text'] = f'Installing  {_per:.2f} %'
                self.install_f.prog_bar['value'] = _per

                if self.extraction_paused:
                    _code = self._install_f_cancel()
                    if _code:
                        _cancel = True
                        break
                    else:
                        self.extraction_paused = False
                        _cancel = False

        except Exception as e:
            self.install_f.place_forget()
            self.fail_ui(e, dir_to_remove=main_out_dir)
        else:
            if _cancel:
                self.install_f.place_forget()
                self.fail_ui('Cancelled by user',
                             dir_to_remove=main_out_dir)
            else:
                """ execution of exes and setting permissions """
                self.install_f.cancel_b['state'] = 'disabled'
                self.protocol('WM_DELETE_WINDOW', self.dummy)

                for __exe in self.main_f.info_f.exe_in_zip:
                    self.install_f.prog_l['text'] = f'executing  {__exe}'
                    __p = Popen([os.path.join(main_out_dir, __exe)])
                    __p.wait()

                if self.main_f.info_f.permissions == 'yes':
                    self.install_f.prog_l['text'] = f'executing  permissions module'
                    set_permissions(main_out_dir)

                self.install_f.prog_bar['value'] = 100
                self.install_f.place_forget()
                self.finish_ui()

    def extract_ui(self, out_dir):
        self.protocol('WM_DELETE_WINDOW', self.install_f_cancel)  # need to be set in every step
        self.install_f.place(relx=0, rely=0, relwidth=1, relheight=1)

        __ext_t = Thread(target=self._extract, args=(out_dir,))
        __ext_t.start()

    def _install_f_cancel(self):
        """ used by _extract to pause the for loop in between """
        return messagebox.askyesno('Confirm Exit',
                                   'This will cancel the setup along with current Progress\n\n        Are you sure to Cancel setup',
                                   parent=self)

    def install_f_cancel(self):
        """ Cancel at install frame """
        self.extraction_paused = True

    def dummy(self, event=None):
        """ dummy func """
        pass

    def fail_ui(self, error, dir_to_remove=None):
        self.fail_f.set_error(error)
        self.protocol('WM_DELETE_WINDOW', self.destroy)  # need to be set in every step
        self.fail_f.place(x=0, y=0, relwidth=1, relheight=1)
        self.fail_f.lift()
        if dir_to_remove and os.path.isdir(dir_to_remove):
            try:
                shutil.rmtree(dir_to_remove)
            except (PermissionError, OSError, Exception):
                pass

    def finish_ui(self):
        self.protocol('WM_DELETE_WINDOW', self.destroy)  # need to be set in every step
        self.finish_f.place(x=0, y=0, relwidth=1, relheight=1)
        self.finish_f.lift()


def load_fonts():
    for font in ext_fonts:
        winfonts.load_font(os.path.join(fonts_dir, font))


def init(setup_info):
    load_fonts()
    installer = Installer(setup_info)
    installer.mainloop()


def exit_on_error(title: str, msg: str):
    error_win = Tk()
    error_win.withdraw()
    messagebox.showerror(title, msg, parent=error_win)
    error_win.destroy()
    sys.exit()


def on_admin_init():
    __setup_info = get_setup_info(os.path.join(src_dir, 'info.cc'))
    if __setup_info:
        init(__setup_info)
    else:
        exit_on_error('Fatal Error', '                      SETUP INITIALISATION FAILED \n\nError Code : Setup Information missing or corrupted')


if __name__ == '__main__':
    if is_admin() or not frozen:
        on_admin_init()
    else:
        run_as_admin(sys.executable)