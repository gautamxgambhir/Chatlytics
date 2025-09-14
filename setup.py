from setuptools import setup, find_packages
import os

def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), 'r', encoding='utf-8') as f:
        return f.read()

def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='chatlytics',
    version='1.0.0',
    author='Gautam Gambhir',
    author_email='ggambhir1919@gmail.com',
    description='Advanced chat conversation analytics and insights platform',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/gautamxgambhir/chatlytics',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Communications :: Chat',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Framework :: Flask'
    ],
    python_requires='>=3.8',
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-flask>=1.2.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0'
        ]
    },
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'chatlytics=app:main'
        ]
    },
    keywords='chat analysis whatsapp instagram analytics insights nlp',
    project_urls={
        'Bug Reports': 'https://github.com/gautamxgambhir/chatlytics/issues',
        'Source': 'https://github.com/gautamxgambhir/chatlytics',
        'Documentation': 'https://chatlytics.readthedocs.io'
    }
)
