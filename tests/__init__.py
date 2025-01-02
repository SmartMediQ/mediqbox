import os, sys

sys.path.append(os.path.join(
  os.path.dirname(__file__), os.pardir,
))

sys.dont_write_bytecode = True

data_dir = os.path.join(
  os.path.dirname(__file__), "data",
)