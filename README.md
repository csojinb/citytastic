Setup
---

First run setup.py in Blender (see below)


How to run in Blender
---

setup.py only needs to be run the first time you start Blender.
After that, the exec command can be repeatedly called to generate new cities.

```filename_test = "C:/projects/citytastic/setup.py"
exec(compile(open(filename_test).read(), filename_test, 'exec'))
filename_test = "C:/projects/citytastic/main.py"
exec(compile(open(filename_test).read(), filename_test, 'exec'))
```