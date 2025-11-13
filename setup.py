"""
Setup do projeto Assistente SQL
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="assistente-sql",
    version="1.0.0",
    author="Equipe de Desenvolvimento",
    description="Sistema inteligente de geração de queries SQL via linguagem natural",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/assistente-sql",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "assistente-sql-api=src.backend.main:main",
        ],
    },
)

