Setup
---
First run setup.py in Blender (see below)


How to run in Blender
---

filename_test = "C:/projects/citytastic/main.py"        <-- that should be an absolute path to the file
exec(compile(open(filename_test).read(), filename_test, 'exec'))
