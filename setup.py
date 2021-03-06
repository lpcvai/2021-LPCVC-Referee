import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name='test_solution',
    version="0.0.0",
    install_requires=requirements,
    author="Matthew Wen",
    author_email="mattwen2018@gmail.com",
    description="Test Solution for CAM2 Drone Team",
    packages=setuptools.find_packages(),
    scripts=["bin/test-solution"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ]
)
