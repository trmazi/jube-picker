import cx_Freeze

executables = [cx_Freeze.Executable("./picker.py")]

cx_Freeze.setup(
    name="JubePicker",
    options={"build_exe": {"packages":["pygame"]}},
    executables = executables
)