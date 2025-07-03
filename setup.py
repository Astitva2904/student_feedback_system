from setuptools import setup, find_packages

setup(
    name="student-feedback-system",
    version="1.0.0",
    description="AI-powered student feedback generation system",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "sentence-transformers==2.2.2",
        "torch>=1.13.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "transformers>=4.21.0"
    ],
    python_requires=">=3.8",
)
