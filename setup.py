from setuptools import setup

setup(
    name='algorithmia-bench',
    version='0.1.1',
    description='Algorithmia Benchmark Tester',
    long_description='Algorithmia Benchmark Tester is a library for testing algorithm performance, comparing algorithms and getting statistical information for each benchmark run.',
    url='http://github.com/algorithmiaio/algorithmia-bench',
    license='MIT',
    author='Algorithmia',
    author_email='support@algorithmia.com',
    packages=['AlgoBench'],
    install_requires=[
        'algorithmia==0.9.3'
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)