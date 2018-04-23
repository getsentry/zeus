from setuptools import setup, find_packages


# we use pip requirements files to improve Docker layer caching


def get_requirements(env):
    with open("requirements-{}.txt".format(env)) as fp:
        return [x.strip() for x in fp.read().split("\n") if not x.startswith("#")]


install_requires = get_requirements("base")
dev_requires = get_requirements("dev")
test_requires = get_requirements("test")

setup(
    name="zeus",
    version="0.1.0",
    packages=find_packages(),
    license="Apache 2.0",
    entry_points={"console_scripts": ["zeus=zeus.cli:main"]},
    long_description=open("README.md").read(),
    extras_require={"dev": dev_requires, "tests": test_requires},
    install_requires=install_requires + dev_requires + test_requires,
)
