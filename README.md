# Course project template

This is a template for course projects. We use [GitHub Classroom](https://classroom.github.com) to administrate our student projects and so you need to sign up for a [GitHub Account](http://github.com).

## Project overview

Please ensure that a brief description of your project is included in the [README.md](https://github.com/HumanCapitalAnalysis/template-course-project/blob/master/README.md), which provides a proper citation of your baseline article. Also, please set up the following badges that allow to easily access your project notebook.

<a href="https://nbviewer.jupyter.org/github/HumanCapitalAnalysis/template-course-project/blob/master/example_project.ipynb"
   target="_parent">
   <img align="center"
  src="https://raw.githubusercontent.com/jupyter/design/master/logos/Badges/nbviewer_badge.png"
      width="109" height="20">
</a>
<a href="https://mybinder.org/v2/gh/HumanCapitalAnalysis/template-course-project/master?filepath=example_project.ipynb"
    target="_parent">
    <img align="center"
       src="https://mybinder.org/badge_logo.svg"
       width="109" height="20">
</a>

## Reproducibility

To ensure full reproducibility of your project, please try to set up a [Travis CI](https://travis-ci.org) as your continuous integration service. An introductory tutorial for [conda](https://conda.io) and [Travis CI](https://docs.travis-ci.com/) is provided [here](https://github.com/HumanCapitalAnalysis/template-course-project/blob/master/tutorial_conda_travis.ipynb). While not at all mandatory, setting up a proper continuous integration workflow is an extra credit that can improve the final grade.

[![Build Status](https://travis-ci.org/HumanCapitalAnalysis/template-course-project.svg?branch=master)](https://travis-ci.org/HumanCapitalAnalysis/template-course-project)

In some cases you might not be able to run parts of your code on  [Travis CI](https://travis-ci.org) as, for example, the computation of results takes multiple hours. In those cases you can add the result in a file to your repository and load it in the notebook. See below for an example code.

```python
# If we are running on TRAVIS-CI we will simply load a file with existing results.
if os.environ['TRAVIS']:
  rslt = pkl.load(open('stored_results.pkl', 'br'))
else:
  rslt = compute_results()

# Now we are ready for further processing.
...
```

However, if you decide to do so, please be sure to provide an explanation in your notebook explaining why exactly this is required in your case.

## Structure of notebook

A typical project notebook has the following structure:

* presentation of baseline article with proper citation and brief summary

* using causal graphs to illustrate the authors' identification strategy

* replication of selected key results

* critical assessment of quality

* independent contribution, e.g. additional external evidence, robustness checks, visualization

There might be good reason to deviate from this structure. If so, please simply document your reasoning and go ahead. Please use the opportunity to review other student projects for some inspirations as well.

## Project Example

The notebook [example_project.ipynb](https://github.com/HumanCapitalAnalysis/template-course-project/blob/master/example_project.ipynb) contains an example project by [Annica Gehlen](https://github.com/amageh) from the 2019 iteration of the [Mircoeconometrics](https://github.com/HumanCapitalAnalysis/microeconometrics) class at Bonn University. It replicates the results from the following paper:

* Lindo, J. M., Sanders, N. J., & Oreopoulos, P. (2010). [Ability, Gender, and Performance Standards: Evidence from Academic Probation](https://www.aeaweb.org/articles?id=10.1257/app.2.2.95). *American Economic Journal: Applied Economics*, 2(2), 95-117.

Lindo et al. (2010) examine the effects of academic probation on student outcomes using a regression discontinuity design. The analysis is based on data from a large Canadian university and evaluates whether academic probation is successful in improving the performance of low scoring students. Consistent with a model of performance standards, the authors find that being placed on probation in the first year of university induces some students to drop out of school while it improves the grades of students who continue their studies. In a more general sense, academic probation can offer insights into how agents respond to negative incentives and the threat of punishment in a real-world context.

## Frequently asked questions and answers

* *Where can I look for publications that provide the data behind their research?* Some journals provide the data for their published articles as data supplements directly on their website. In addition, the [Replication Wiki](http://replication.uni-goettingen.de/wiki/index.php/Main_Page)  and the [Harvard Dataverse](https://dataverse.harvard.edu) compile a lot such information.

* *What are other useful resources for research data?* There is a tremendous amount of data available online. For example, MDRC provides a host of data files for public use [here](https://www.mdrc.org/available-public-use-files) from the evaluation of public policy initiatives. More generally, [Google Dataset Search](https://datasetsearch.research.google.com) allows to look for all kinds of online data. 

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/HumanCapitalAnalysis/template-course-project/blob/master/LICENSE)
