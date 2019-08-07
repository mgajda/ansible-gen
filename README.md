# Ansible script generator

Goal of this script is to automate the simples Ansible deployments over AWS, by taking just
shell history, and converting it into Ansible deployment script.

Example inputs are in [inputs/ directory](inputs/).

# Goal

Create easily maintainable Python script, that takes Bash shell history, and converts it into
Ansible deployment script.

It should match patterns line by line, and allow easy extension to new patterns.

When pattern is not recognized - it should issue a warning.

## Interface
```bash
ansible-gen.py .bash_history -o ansible.yml
```
Additional options:
* `--local ec2-instance` - the following history file was recorded locally (not remotely),
and refers to remote as `ec2-instance`
* `--remote` - the following history file was recorded remotely (default).

## Configuration commands supported
### Command supported by Ansible modules on remote
Remote system commands supported should include at least:
* `cat` to `crontab`, `/etc/fstab`, and `authorized_keys`
* `pip`
* `cd`
* `mkdir`
* `rm` and `rm -rf`
* `apt-get update`, `apt-get upgrade`, `apt-get dist-upgrade`
* `apt-get install`
* `mount`
* `curl https://... | sh` should be supported to prime installation of essential tools:
  - Stack
  - HomeBrew
  - Nix

### On local
* `scp`

### Package management functionality on the remote
* `npm install`, and `npm update`
* `bower install`, and `bower update`
* `cp` service file to `nginx` directory
* `docker run`, and `docker exec`
* `brew install` and `brew cask install` should install respective packages
* `mas install` should install MacOS-X Apple Store CLi with `brew` and then run command

### Additional package management options
* `--git <directory>` option should visit all (direct) subdirectories of a given directory, and add commands to clone them on the new machine (in same directory relative to `$HOME`, example directory `input/git`)
* `--brew` option should run `brew list` to list installed packages, and use Homebrew module in Ansible to install them (example file: `input/mac/brew.list`)
* `--mas` option should run `mas list` command to list installed Mac App Store apps and install them with `mas install $APPID` (example file: `input/mac/mas.list`)
* `--npm` option should list Node packages installed directly (but not their dependencies!), and install them (example file: `input/npm.list`)

### Git building

If Git repo has a build script on the script below, we should automatically build it.
In the background, since it may take long time:
* `stack.yaml` -> `stack build`
* `pier.yaml` -> `pier build`
* `default.nix` -> `nix-shell --pure default.nix`

## Ideal use case

User should be able to copy his local, and remote `.bash_history` file, remove unnecessary commands,
and run the `ansible-gen.py` to get fully functional template of ansible script.

### Why

A lot of configuration tasks do not require tuning, and are done just a few times.
Investing in development of Ansible scripts to run them seems a waste of time.

# AWS functionality

We would also like to copy&paste AWS instance config we make in GUI, and then put it into Git repo.
Then we want to setup the instance from scratch with the very Ansible script we generate.

[And we already know instance name, so we should be able to pull Amazon config easily, don't we?]

# Mac support

https://github.com/maybevoid/maybevoid.com.git

# Future Linux support

There will be additional script that performs unattended Linux install before running the generated configuration script.
