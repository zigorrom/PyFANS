from setuptools import setup, find_packages

# import build_ui
try:
    from pyqt_distutils.build_ui import build_ui
    cmdclass = {'build_ui': build_ui}
except ImportError:
    print("import error")
    build_ui = None  # user won't have pyqt_distutils when deploying
    cmdclass = {}

setup(name='PyFANS',
    version='2.1.3',
    description='Python Fully Automated Noise Setup',
    author='Ihor Zadorozhnyi',
    author_email='zigorrom@gmail.com',
    url='https://github.com/zigorrom/PyFANS/tree/PyFANS_v2.1.3.1',
    cmdclass=cmdclass,
    packages=find_packages()
)