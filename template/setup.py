import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name="test-suite",
    version="0.0.1",
    author="Denis",
    description="This is my application",
    long_description=long_description,
    long_decription_content_type="text/markdown",
    url='ssh://git@github:9999/test_suite.git',
    packages=setuptools.find_packages(),
    install_requires=[
        'wget',
        'HTMLTestRunner-rv=1.0.17'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': ['testsuite=test_suite.test_suite:main']
    },
    include_package_data=True
)

"""
The build_package.py must copy ALL the .py, .jar, .yaml, .json, and any data files needed by the app files to the testsuite_pkg directory.
1. cd to the build directory.
2. Run python build_package.py - this must be written to create the testsuite_pkg.
3. cd to the testsuite_pkg directory.
4. Run python setup.py sdist bdist_wheel
5. cd to the testsuite_pkg/dist directory.
6. Run pip unistall test-suite
7. commit and push any changes.
8. Run pip install test_suite-0.0.1-py3-none-any.whl
9. Run testsuite -h or -l to make sure it installed.
"""