frida-gadget
====

|Py-Versions| |Versions| |Conda-Forge-Status| |Docker| |Snapcraft|

|Build-Status| |Coverage-Status| |Branch-Coverage-Status| |Codacy-Grade| |Libraries-Rank| |PyPI-Downloads|

|LICENCE| |OpenHub-Status| |binder-demo| |awesome-python|

``frida-gadget`` is a APK patcher, for  `frida gadget <https://frida.re/docs/gadget/>`__.
I hope this will help you to patch APK to using the Frida gadget.

.. |Logo| image:: https://img.tqdm.ml/logo.gif
.. |Screenshot| image:: https://img.tqdm.ml/tqdm.gif
.. |Video| image:: https://img.tqdm.ml/video.jpg
   :target: https://tqdm.github.io/video
.. |Slides| image:: https://img.tqdm.ml/slides.jpg
   :target: https://tqdm.github.io/PyData2019/slides.html
.. |Merch| image:: https://img.tqdm.ml/merch.jpg
   :target: https://tqdm.github.io/merch
.. |Build-Status| image:: https://img.shields.io/github/workflow/status/ksg97031/frida-gadget/Test/master?logo=GitHub
   :target: https://github.com/ksg97031/frida-gadget/actions?query=workflow%3ATest
.. |Coverage-Status| image:: https://img.shields.io/coveralls/github/ksg97031/frida-gadget/master?logo=coveralls
   :target: https://coveralls.io/github/ksg97031/frida-gadget
.. |Branch-Coverage-Status| image:: https://codecov.io/gh/ksg97031/frida-gadget/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/ksg97031/frida-gadget
.. |Codacy-Grade| image:: https://app.codacy.com/project/badge/Grade/3f965571598f44549c7818f29cdcf177
   :target: https://www.codacy.com/gh/ksg97031/frida-gadget/dashboard
.. |CII Best Practices| image:: https://bestpractices.coreinfrastructure.org/projects/3264/badge
   :target: https://bestpractices.coreinfrastructure.org/projects/3264
.. |GitHub-Status| image:: https://img.shields.io/github/tag/ksg97031/frida-gadget.svg?maxAge=86400&logo=github&logoColor=white
   :target: https://github.com/ksg97031/frida-gadget/releases
.. |GitHub-Forks| image:: https://img.shields.io/github/forks/ksg97031/frida-gadget.svg?logo=github&logoColor=white
   :target: https://github.com/ksg97031/frida-gadget/network
.. |GitHub-Stars| image:: https://img.shields.io/github/stars/ksg97031/frida-gadget.svg?logo=github&logoColor=white
   :target: https://github.com/ksg97031/frida-gadget/stargazers
.. |GitHub-Commits| image:: https://img.shields.io/github/commit-activity/y/ksg97031/frida-gadget.svg?logo=git&logoColor=white
   :target: https://github.com/ksg97031/frida-gadget/graphs/commit-activity
.. |GitHub-Issues| image:: https://img.shields.io/github/issues-closed/ksg97031/frida-gadget.svg?logo=github&logoColor=white
   :target: https://github.com/ksg97031/frida-gadget/issues?q=
.. |GitHub-PRs| image:: https://img.shields.io/github/issues-pr-closed/ksg97031/frida-gadget.svg?logo=github&logoColor=white
   :target: https://github.com/ksg97031/frida-gadget/pulls
.. |GitHub-Contributions| image:: https://img.shields.io/github/contributors/ksg97031/frida-gadget.svg?logo=github&logoColor=white
   :target: https://github.com/ksg97031/frida-gadget/graphs/contributors
.. |GitHub-Updated| image:: https://img.shields.io/github/last-commit/ksg97031/frida-gadget/master.svg?logo=github&logoColor=white&label=pushed
   :target: https://github.com/ksg97031/frida-gadget/pulse
.. |Gift-Casper| image:: https://img.shields.io/badge/dynamic/json.svg?color=ff69b4&label=gifts%20received&prefix=%C2%A3&query=%24..sum&url=https%3A%2F%2Fcaspersci.uk.to%2Fgifts.json
   :target: https://cdcl.ml/sponsor
.. |Versions| image:: https://img.shields.io/pypi/v/tqdm.svg
   :target: https://tqdm.github.io/releases
.. |PyPI-Downloads| image:: https://img.shields.io/pypi/dm/tqdm.svg?label=pypi%20downloads&logo=PyPI&logoColor=white
   :target: https://pepy.tech/project/tqdm
.. |Py-Versions| image:: https://img.shields.io/pypi/pyversions/tqdm.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/tqdm
.. |Conda-Forge-Status| image:: https://img.shields.io/conda/v/conda-forge/tqdm.svg?label=conda-forge&logo=conda-forge
   :target: https://anaconda.org/conda-forge/tqdm
.. |Snapcraft| image:: https://img.shields.io/badge/snap-install-82BEA0.svg?logo=snapcraft
   :target: https://snapcraft.io/tqdm
.. |Docker| image:: https://img.shields.io/badge/docker-pull-blue.svg?logo=docker&logoColor=white
   :target: https://hub.docker.com/r/ksg97031/frida-gadget
.. |Libraries-Rank| image:: https://img.shields.io/librariesio/sourcerank/pypi/tqdm.svg?logo=koding&logoColor=white
   :target: https://libraries.io/pypi/tqdm
.. |Libraries-Dependents| image:: https://img.shields.io/librariesio/dependent-repos/pypi/tqdm.svg?logo=koding&logoColor=white
    :target: https://github.com/ksg97031/frida-gadget/network/dependents
.. |OpenHub-Status| image:: https://www.openhub.net/p/tqdm/widgets/project_thin_badge?format=gif
   :target: https://www.openhub.net/p/tqdm?ref=Thin+badge
.. |awesome-python| image:: https://awesome.re/mentioned-badge.svg
   :target: https://github.com/vinta/awesome-python
.. |LICENCE| image:: https://img.shields.io/pypi/l/tqdm.svg
   :target: https://raw.githubusercontent.com/ksg97031/frida-gadget/master/LICENCE
.. |DOI| image:: https://img.shields.io/badge/DOI-10.5281/zenodo.595120-blue.svg
   :target: https://doi.org/10.5281/zenodo.595120
.. |binder-demo| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/ksg97031/frida-gadget/master?filepath=DEMO.ipynb
.. |Screenshot-Jupyter1| image:: https://img.tqdm.ml/jupyter-1.gif
.. |Screenshot-Jupyter2| image:: https://img.tqdm.ml/jupyter-2.gif
.. |Screenshot-Jupyter3| image:: https://img.tqdm.ml/jupyter-3.gif
.. |README-Hits| image:: https://caspersci.uk.to/cgi-bin/hits.cgi?q=tqdm&style=social&r=https://github.com/ksg97031/frida-gadget&l=https://img.tqdm.ml/favicon.png&f=https://img.tqdm.ml/logo.gif
   :target: https://caspersci.uk.to/cgi-bin/hits.cgi?q=tqdm&a=plot&r=https://github.com/ksg97031/frida-gadget&l=https://img.tqdm.ml/favicon.png&f=https://img.tqdm.ml/logo.gif&style=social
