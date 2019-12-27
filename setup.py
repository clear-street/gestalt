from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='gestalt-cfg',
      version='1.0.0',
      description='A sensible configuration library for Python',
      long_description=readme(),
      long_description_content_type="text/markdown",
      url='https://github.com/clear-street/gestalt',
      author='Clear Street',
      author_email='engineering@clearstreet.io',
      license='MIT',
      packages=['gestalt'],
      install_requires=['mypy==0.720', 'mypy-extensions==0.4.1'],
      python_requires='>=3.6',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries',
          'Programming Language :: Python :: 3 :: Only',
          'Operating System :: OS Independent',
      ])
