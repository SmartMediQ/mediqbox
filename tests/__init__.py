import os, sys

from dotenv import load_dotenv

sys.path.append(os.path.join(
  os.path.dirname(__file__), os.pardir,
))

sys.dont_write_bytecode = True

data_dir = os.path.join(
  os.path.dirname(__file__), "data",
)

load_dotenv()