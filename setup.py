import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name = 'eoepca-scim',
  version = '2.7.3',
  author = 'EOEPCA',
  author_email = 'eoepca.systemteam@telespazio.com',
  description = 'Python library to interact with SCIM protocol',
  long_description = long_description,
  long_description_content_type="text/markdown",
  url = 'https://github.com/EOEPCA/um-common-scim-client ',
  packages=setuptools.find_packages(),
  license='apache-2.0',
  keywords = ['SCIM', 'Client', 'EOEPCA','user','management'],
  classifiers=[
    'Development Status :: 3 - Alpha',                      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
  ],
  python_requires='>=3.6',
)
