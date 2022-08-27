......................................................  Installer Module (RC @Nov 12, 2021)  ..................................................

# A Custom Installer Module for my Project Releases

Any release installation requires 2 files listed below

# Information file

   1. Name: 'info.cc'
   2. Content: Python Dictionary dumped by pickle in form  

  {  
     'zip_name' : 'main.zip',  
     'exe_in_zip': ['intro.exe', 'reg.exe', ],  (list of exe's to be executed after extraction, paths relative to zip)  
     'soft_name': 'Twilight',  
     'version': '7.9.8',  
     'soft_author': 'Rc',  
     'soft_des': 'description'  
     'uninstall_key_name': 'Twilight',  (in windows registry, to cross check installation)  
     'main_exe_name': 'Twilight',    (main exe name to cross check installation)  
     'permissions' : 'no'   ('no' or 'yes', to allow read and write permissions in install dir)  
  }
  
# Main Data Zip file

   1. Name: as defined in info.cc
   2. Content: all release folders and files to be extracted
   2. zip should NOT contain root directory, it will be created automatically

# Usage

1. "installer.exe" and "sdk" folder (contains resources) should be in same directory
1. Copy Information file and Main data zip file in "sdk/src" folder
3. If previous installation is found (by checking uninstall registry info and main_exe given in info.cc),
   uninstall option will execute uninstaller,exe with '-force' arg (to avoid any ui)

 