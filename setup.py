from setuptools import setup

setup(
    name='facebot',
    version='0.0.9',
    author='davidyen1124',
    author_email='davidyen1124@gmail.com',
    packages=['facebot'],
    url='https://github.com/davidyen1124/Facebot',
    description='Unofficial facebook api',
    license='MIT',
    install_requires=[
        'lxml==3.3.5',
        'requests==2.3.0'
    ],
)
