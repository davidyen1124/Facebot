from setuptools import setup

license = open('LICENSE').read()

setup(
    name='facebot',
    version='0.0.1',
    author='davidyen1124',
    author_email='davidyen1124@gmail.com',
    packages=['facebot'],
    url='https://github.com/davidyen1124/Facebot',
    description='Unofficial facebook api',
    long_description=open('README.MD').read(),
    license=license,
    install_requires=[
        'lxml==3.3.5',
        'requests==2.3.0'
    ],
)
