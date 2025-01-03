# Python script to generate .env.sample from .env
import os

def gen_env_tmpl(relative_dir: str):
  # Define paths to .env and .env.sample files
  dir = os.path.join(os.path.dirname(__file__), relative_dir)
  env_path = os.path.join(dir, ".env")
  env_tmpl_path = os.path.join(dir, ".env.tmpl")

  # Open .env file and read the lines
  with open(env_path, "r") as env_fp:
    lines = env_fp.readlines()

  # Open (or create) .env.sample file in write mode
  with open(env_tmpl_path, "w") as env_tmpl_fp:
    for line in lines:
      if "=" in line:
        # Split the line at the first equals sign
        key, _ = line.split("=", 1)
        # Write the key with an empty value or a dummy value to .env.sample file
        env_tmpl_fp.write(f"{key}=\n")
      else:
        env_tmpl_fp.write(line)

  print(f".env.tmpl has been generated under '{relative_dir}'.")
  
relative_dirs = ["tests"]
for relative_dir in relative_dirs:
  gen_env_tmpl(relative_dir)