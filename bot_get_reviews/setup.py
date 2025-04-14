import setuptools
import sys


project_name = "reviews_bot"


if '--project_name' in sys.argv:
     project_name_idx = sys.argv.index('--project_name')
     project_name = sys.argv[project_name_idx + 1]
     sys.argv.remove('--project_name')
     sys.argv.pop(project_name_idx)


setuptools.setup(name=project_name)
