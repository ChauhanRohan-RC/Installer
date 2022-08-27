import os
import sys
import pickle


# only for testing

main_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(os.path.realpath(__file__)))

soft_name = 'Twilight'
version = '8.6.0'
author = 'Rohan Chauhan'
description = 'asdfasfasf'

info_dic = {'zip_name': 'main.zip',
            'exe_in_zip': [C.RegExeName + '.exe', ],
            'soft_name': C.ExeName,
            'version': C.Version,
            'soft_author': C.Author,
            'soft_des': C.Description,
            'uninstall_key_name': C.ExeName,
            'main_exe_name': C.ExeName,
            'permissions': 'no'}

with open(os.path.join(C.MainDir, 'info.cc'), 'wb+') as _f:
    pickle.dump(info_dic, _f)