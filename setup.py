import setuptools
with open("README.md", "r") as f:
	long_description = f.read()
setuptools.setup(
	name="c2logic",
	version="0.1",
	descripton="Compiles C code to Mindustry logic.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	packages=["c2logic"],
	license="MIT",
	author="SuperStormer",
	url="https://github.com/SuperStormer/c2logic",
	project_urls={"Source Code": "https://github.com/SuperStormer/c2logic"},
	headers=["include/builtins.h"],
	entry_points={"console_scripts": ["c2logic=c2logic.compiler:main"]},
	install_requires=["pycparser~=2.20"]
)