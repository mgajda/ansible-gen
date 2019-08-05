# Stage 2 functionality - unattended Mac workstation install

## Generating input:
1. That lists the /Applications and homebrew packages installed into format as in files `Cellar` and `Applications`
  - removing system applications and library dependencies from the list
  - warning about "unsupported" applications
2. Lists git repos as in file `Projects`:
  - remote
  - branch name
  - directory

3. Additionally we have a list of user directories to copy (like `.config`),
   and we compress them into .tgz.

## Setup from given input

First we make an unattended preconfiguration of Mac OS X workstation.

Then we get Ansible to:
  - clone *and* build projects with `stack` (if `stack.yaml` is present)
  - install applications from homebrew packages
  - for those that cannot be installed by homebrew - install by AppleScript
  - take a compressed image of enumerated directories and unpack at the given location

## Setup on Linux machine

Same for setup on Linux dev machine:
* option of using debian-installer (fully unattended install, generated from install log)
* and then Ansible setup script 
