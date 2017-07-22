# Ansible script generator

Goal of this script is to automate the simples Ansible deployments over AWS, by taking just
shell history, and converting it into Ansible deployment script.

Example inputs are in [inputs/ directory](inputs/).

# Goal

Create easily maintainable Python script, that takes Bash shell history, and converts it into
Ansible deployment script.

It should match patterns line by line, and allow easy extension to new patterns.

When pattern is not recognized - it should issue a warning.
