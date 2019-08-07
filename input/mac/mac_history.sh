#xcode-select --install
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" # install brew
brew cask install firefox gimp dropbox docker mactex skype sublime paintcode libreoffice microsoft-office atomkeybase meld inkscape google-chrome karabiner-elements
brew cask install ansible aspell awscli azure-cli chrome-cli cmake coreutils diction docker-completion docker-machine-completion fswatch git git-annex git-lfs glib graphviz hunspell jq md5sha1sum mmv mtr neovim openssl pandoc pstree python redis sloccount sqlite swi-prolog tidy-html5 tmate tmpreaper watchman wget xsv xz z3
mas install 414030210 # LimeChat
mas install 841285201 # Haskell (1.6.1)
mas install 497799835 # Xcode (10.3)
mas install 921923693 # LibreOffice Vanilla (6.2.5000)
# NixOS
nix-build https://github.com/LnL7/nix-darwin/archive/master.tar.gz -A installer
./result/bin/darwin-installer
cd ~/exp/nix
ln -s ~/.nixpkgs/darwin-configuration.nix ~/exp/nix/darwin-configuration.nix
darwin-rebuild
darwin-switch # only if rebuild succeeded


