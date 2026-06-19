from setuptools import setup
from pathlib import Path

readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="rds-connection-manager",
    version="1.0.0",
    description="AWS RDS connection manager with IAM authentication and logging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/rds-connection-manager",
    license="MIT",
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: System :: Systems Administration",
    ],
    
    project_urls={
        "Bug Reports": "https://github.com/yourusername/rds-connection-manager/issues",
        "Source": "https://github.com/yourusername/rds-connection-manager",
    },
    
    py_modules=["connect_rds_manager"],
    python_requires=">=3.8",
    
    install_requires=[
        "boto3>=1.28.0",
    ],
    
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "mypy>=1.0.0",
            "pylint>=2.16.0",
            "black>=23.0.0",
        ],
    },
    
    entry_points={
        "console_scripts": [
            "rds-connect=connect_rds_manager:main",
        ],
    },
    
    include_package_data=True,
    
    keywords=[
        "aws", "rds", "database", "connection", "iam",
        "postgresql", "devops",
    ],
)
