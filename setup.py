from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='gestalt-cfg',
      version='1.0.7',
      description='A sensible configuration library for Python',
      long_description=readme(),
      long_description_content_type="text/markdown",
      url='https://github.com/clear-street/gestalt',
      author='Clear Street',
      author_email='engineering@clearstreet.io',
      license='MIT',
      packages=['gestalt'],
      python_requires='>=3.6',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Libraries',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3 :: Only',
          'Operating System :: OS Independent',
      ])
