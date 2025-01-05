from setuptools import setup, find_packages

setup(
    name='unfold-admin-django-cloned',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.0',
        # List other dependencies here
    ],
    description='A custom admin interface for Django',
    author='Your Name',
    author_email='info@muhamedjamal.com',
    url='https://github.com/mohamed-cpp/django-unfold',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        # Add other classifiers as needed
    ],
)
