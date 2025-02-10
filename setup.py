# azure_oauth/setup.py

"""_summary_
"""

from setuptools import setup, find_packages #type: ignore

with open('requirements.txt', encoding='utf-8-sig') as f:
    requirements = [
        line.strip() for line in
        f.read().splitlines()
    ]

with open('README.md', encoding='utf-8') as f:
    long_desc = f.read()

setup(
    name="azure_oauth",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    description="Oauth2 authorization",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="Abdimalik Abdi Mohamed",
    author_email="Abdimalik.AbdiMohamed@apollo_underwriting.com",
    url="https://github.com/yourusername/your-package",
    python_requires='>=3.6',
)
