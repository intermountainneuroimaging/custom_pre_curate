#!/usr/bin/env bash 

IMAGE=lsherbakov/custom-pre-curate:0.1.2

# Command:
docker run \
	-e FLYWHEEL=/flywheel/v0\
	-e GPG_KEY=E3FF2839C048B25C084DEBE9B26995E310250568\
	-e LANG=C.UTF-8\
	-e PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\
	-e PYTHON_GET_PIP_SHA256=e235c437e5c7d7524fbce3880ca39b917a73dc565e0c813465b7a7a329bb279a\
	-e PYTHON_GET_PIP_URL=https://github.com/pypa/get-pip/raw/38e54e5de07c66e875c11a1ebbdb938854625dd8/public/get-pip.py\
	-e PYTHON_PIP_VERSION=22.0.4\
	-e PYTHON_SETUPTOOLS_VERSION=57.5.0\
	-e PYTHON_VERSION=3.8.13\
	-v /Users/lenasherbakov/Documents/work/fw_gears/custom_pre_curate/custom-pre-curate-0.1.2-6269543c75975922d1f28b77/input:/flywheel/v0/input\
	-v /Users/lenasherbakov/Documents/work/fw_gears/custom_pre_curate/custom-pre-curate-0.1.2-6269543c75975922d1f28b77/output:/flywheel/v0/output\
	-v /Users/lenasherbakov/Documents/work/fw_gears/custom_pre_curate/custom-pre-curate-0.1.2-6269543c75975922d1f28b77/work:/flywheel/v0/work\
	-v /Users/lenasherbakov/Documents/work/fw_gears/custom_pre_curate/custom-pre-curate-0.1.2-6269543c75975922d1f28b77/config.json:/flywheel/v0/config.json\
	-v /Users/lenasherbakov/Documents/work/fw_gears/custom_pre_curate/custom-pre-curate-0.1.2-6269543c75975922d1f28b77/manifest.json:/flywheel/v0/manifest.json\
	$IMAGE
