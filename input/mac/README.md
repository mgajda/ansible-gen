# Stage 2 functionality - unattended Mac workstation install

We need a script:
1. That lists the /Applications and homebrew packages installed into format as in files `Cellar` and `Applications`
  - removing system applications and library dependencies from the list
  - warning about "unsupported" applications
2. Lists git repos as in file `Projects`:
  - remote
  - branch name
  - directory

3. Then we get Ansible to:
  - clone *and* build projects with `stack` (if `stack.yaml` is present)
  - install applications from homebrew packages
  - for those that cannot be installed by homebrew - install by AppleScript

