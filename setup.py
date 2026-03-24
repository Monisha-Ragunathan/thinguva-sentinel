from setuptools import setup, find_packages

setup(
    name="thinguva-sentinel",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",
        "sqlalchemy>=2.0",
        "fastapi>=0.115.0",
        "uvicorn>=0.42.0",
        "scikit-learn>=1.6.0",
        "numpy>=2.0.0",
        "httpx>=0.28.0",
        "reportlab>=4.0.0",
    ],
    python_requires=">=3.11",
    author="Thinguva",
    description="Agent Governance and Reliability Platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Monisha-Ragunathan/thinguva-sentinel",
)