import os.path
import re
from typing import Final

import setuptools


MODULE_NAME: Final = "pytest-md-report"
REPOSITORY_URL: Final = f"https://github.com/thombashi/{MODULE_NAME:s}"
REQUIREMENT_DIR: Final = "requirements"
ENCODING: Final = "utf8"

pkg_info: dict[str, str] = {}


def get_release_command_class() -> dict[str, type[setuptools.Command]]:
    try:
        from releasecmd import ReleaseCommand
    except ImportError:
        return {}

    return {"release": ReleaseCommand}


def make_long_description() -> str:
    # ref: https://github.com/pypa/readme_renderer/issues/304
    re_exclude = re.compile(r"\s*:scale:\s*\d+")

    with open("README.rst", encoding=ENCODING) as f:
        return "".join([line for line in f if not re_exclude.search(line)])


with open(os.path.join(MODULE_NAME.replace("-", "_"), "__version__.py")) as f:
    exec(f.read(), pkg_info)

with open(os.path.join(REQUIREMENT_DIR, "requirements.txt")) as f:
    INSTALL_REQUIRES = [line.strip() for line in f if line.strip()]

with open(os.path.join(REQUIREMENT_DIR, "test_requirements.txt")) as f:
    TESTS_REQUIRES = [line.strip() for line in f if line.strip()]


setuptools.setup(
    name=MODULE_NAME,
    url=REPOSITORY_URL,
    author=pkg_info["__author__"],
    author_email=pkg_info["__email__"],
    description="A pytest plugin to generate test outcomes reports with markdown table format.",
    include_package_data=True,
    keywords=["pytest", "plugin", "markdown"],
    license=pkg_info["__license__"],
    long_description=make_long_description(),
    long_description_content_type="text/x-rst",
    packages=setuptools.find_packages(),
    package_data={MODULE_NAME: ["py.typed"]},
    project_urls={
        "Changelog": f"{REPOSITORY_URL:s}/releases",
        "Source": REPOSITORY_URL,
        "Tracker": f"{REPOSITORY_URL:s}/issues",
    },
    python_requires=">=3.9",
    install_requires=INSTALL_REQUIRES,
    extras_require={"test": TESTS_REQUIRES},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Markup :: Markdown",
        "Typing :: Typed",
    ],
    cmdclass=get_release_command_class(),
    zip_safe=False,
    entry_points={
        "pytest11": [
            "pytest-md-report = pytest_md_report.plugin",
        ]
    },
)
