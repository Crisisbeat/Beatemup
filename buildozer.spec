[app]

# (str) Title of your application
title = BeatEmUp Prototype

# (str) Package name
package.name = beatemup

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,gif,wav,mp3,ttf

# (list) Application requirements
requirements = python3,hostpython3,pygame,pillow


# (str) Custom source folders for requirements
# packageless_requirements = 

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientations (one of landscape, sensorLandscape, portrait or all)
orientation = landscape

# (list) Permissions
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (int) Android API to use
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
#android.ndk = 23b

# (bool) use buildozer/venv
buildozer.use_venv = 1

# (list) Android add_jars
#android.add_jars = foo.jar,bar.jar,baz.jar

# (list) Android additional libraries
#android.add_src = foo,bar

# (list) Android NDK directory
#android.ndk_path = 

# (list) Android SDK directory
#android.sdk_path = 

# (str) ANT directory
#android.ant_path = 

# (str) Android entry point, default is to use start.py
#android.entrypoint = main.py

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

# (list) Gradle dependencies
#android.gradle_dependencies = 

# (list) Java classes to add as activities to the manifest.
#android.add_activities = com.example.ExampleActivity

# (str) OUYA Console category. Should be one of GAME or APP
#android.ouya.category = GAME

# (list) Android additional libraries to copy into libs/armeabi
#android.copy_libs = 

# (bool) skip update of the Android SDK
#android.skip_update = False

# (bool) display warning if sdks are not found
#android.log_level = 2

# (bool) Copy library instead of making a lib dir
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (list) Android application meta-data to set (key=value format)
#android.meta_data = 

# (list) Android library project for adding support for specific Android libraries
#android.library_references = 

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, can be a variable name, or absolute path
bin_dir = ./bin
