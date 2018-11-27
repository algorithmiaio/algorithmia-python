import os
import json
import templates
from os.path import join
from os.path import abspath
from enum import Enum
from jinja2 import FileSystemLoader, Environment
from shutil import rmtree, copytree, copy
from tempfile import mkdtemp
import templates

DEFAULT_TEMPLATE_BASE_PATH = "{}/templates".format(os.path.split(__file__)[0])

class TemplateBasedAlgorithm:
  def __init__(self, algorithm_publisher=None, template_location=None):
    self.apub = algorithm_publisher
    self.template_location = template_location

  def list(self):
    if self.template_location is None:
      return templates.list_available_templates()
    return []

  class ExportMode(Enum):
    LOCAL=1,
    COMMIT=2,
    PUBLISH=3

  def export(self, template, algo_name, mode=ExportMode.LOCAL, context=None, build_location=None):
    if template not in self.list():
      raise Exception("Template: {} is not supported. Supported templates are {}".format(template, DEFAULT_SUPPORTED_TEMPLATES))

    template_path = templates.get_template_path(template)

    env = Environment(loader=FileSystemLoader(template_path))

    if not context:
      with open('{}/default_context.json'.format(template_path)) as f:
        context = json.load(f)

    # Get the generated code.
    algo = env.get_template('Algorithm.py').render(data=context)
    requirements = env.get_template('requirements.txt').render(data=context)

    # Create the build
    build_path = self.__create_build(algo_name, template, template_path, algo, requirements, build_location=build_location)

    if mode == self.ExportMode.LOCAL:
      return build_path

    # Create a new algorithm if one does not exist
    self.apub.create_algorithm(algo_name)

    # Clone into a local repo
    local_repo_location = mkdtemp()+'/'+algo_name
    cloned_repo = self.apub.git_clone(algo_name, local_repo_location = local_repo_location)

    # Copy over the build into the lcoal repo
    changed_files = self.__copy_to_repo(build_path, local_repo_location, algo_name)

    # Push the changes
    self.apub.git_push(cloned_repo, changed_files, commit_message='Algorithm created based on template: {}'.format(template))

    if mode == self.ExportMode.PUBLISH:
      published_algo = self.apub.publish_algorithm(algo_name)
      return published_algo
    else:
      return cloned_repo

  def __create_build(self, algo_name, template_name, template_path, algo, requirements, build_location = None, template_base = DEFAULT_TEMPLATE_BASE_PATH):
    if build_location is None:
      build_location = mkdtemp()
    build_path = join(build_location, template_name)
    rmtree(build_path, ignore_errors=True)
    os.makedirs(build_path)
    os.symlink(abspath(join(template_base,'helpers')), abspath(join(build_path, 'helpers')))
  
    # Symlink or create (if one does not exist in the template) a data path.
    src_data_path = abspath(join(template_path, 'data'))
    dst_data_path = abspath(join(build_path, 'data'))
    if os.path.isdir(src_data_path):
      os.symlink(src_data_path, dst_data_path)
    else:
      os.mkdir(dst_data_path)

    os.mkdir(join(build_path, 'src'))

    with open(join(build_path, 'src', '{}.py'.format(algo_name)), 'w') as f:
      f.write(algo)
    with open(join(build_path, 'requirements.txt'), 'w') as f:
      f.write(requirements)
    return build_path

  def __copy_to_repo(self, build_location, repo_location, algo_name):
    rmtree(join(repo_location, 'data'), ignore_errors=True)
    rmtree(join(repo_location, 'helpers'), ignore_errors=True)

    copy(join(build_location, 'src', '{}.py'.format(algo_name)), join(repo_location, 'src'))
    copy(join(build_location, 'requirements.txt'), repo_location)
    copytree(join(build_location, 'data'), join(repo_location, 'data'), symlinks=True)
    copytree(join(build_location, 'helpers'), join(repo_location, 'helpers'), symlinks=True)

    return ['src/{}.py'.format(algo_name), 'data', 'helpers', 'requirements.txt']
