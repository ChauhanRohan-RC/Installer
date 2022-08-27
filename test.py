from subprocess import Popen

p = Popen([r"C:\Program Files (x86)\Twilight 8.7.5\Uninstall.exe", '-force'])
p.wait()
print('return code : ', p.returncode)
