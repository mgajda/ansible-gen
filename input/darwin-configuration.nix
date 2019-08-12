{ config, pkgs, ... }:

{
  # List packages installed in system profile. To search by name, run:
  # $ nix-env -qaP | grep wget
  environment.systemPackages =
    [ pkgs.vim
      pkgs.ansible
      pkgs.ansible-lint
      pkgs.aspell
      pkgs.aspellDicts.en
      pkgs.aspellDicts.en-computers
      pkgs.aspellDicts.en-science
      pkgs.awscli
      # pkgs.azure-cli
      pkgs.cmake
      pkgs.diction
      pkgs.git-latexdiff
      pkgs.git-lfs
      pkgs.git
      # pkgs.haskell-ci
      pkgs.pandoc
      pkgs.graphviz
      pkgs.jq
      pkgs.neovim
      pkgs.openssl_1_1
      pkgs.pandoc
      pkgs.pstree
      pkgs.aws_shell
      pkgs.redis
      pkgs.sloccount
      pkgs.sqlite
      #pkgs.swiProlog
      pkgs.tmate
      pkgs.watchman
      pkgs.wget
      pkgs.xsv
      # pkgs.z3
      pkgs.fontconfig
      pkgs.texlive.combined.scheme-full
    ];
  nixpkgs.config.allowUnfree = true;

  # Use a custom configuration.nix location.
  # $ darwin-rebuild switch -I darwin-config=$HOME/.config/nixpkgs/darwin/configuration.nix
  # environment.darwinConfig = "$HOME/.config/nixpkgs/darwin/configuration.nix";

  # Auto upgrade nix package and the daemon service.
  # services.nix-daemon.enable = true;
  # nix.package = pkgs.nix;

  # Create /etc/bashrc that loads the nix-darwin environment.
  programs.bash.enable = true;
  # programs.zsh.enable = true;
  # programs.fish.enable = true;

  # Used for backwards compatibility, please read the changelog before changing.
  # $ darwin-rebuild changelog
  system.stateVersion = 4;

  # You should generally set this to the total number of logical cores in your system.
  # $ sysctl -n hw.ncpu
  nix.maxJobs = 2;
  nix.buildCores = 2;
  #----=[ Fonts ]=----#
  fonts = {
    #enableDefaultFonts = true; # NixOS
    enableFontDir = true;
    fonts = [ 
      pkgs.corefonts
      pkgs.dejavu_fonts
      pkgs.ubuntu_font_family
    ];

    #fontconfig = { # NixOS
    #  penultimate.enable = true;
    #  defaultFonts = {
    #    serif = [ "Ubuntu" "DejaVu"];
    #    sansSerif = [ "Ubuntu" "DejaVu" ];
    #    monospace = [ "Ubuntu" "Arial" ];
    #  };
    #};
  };
}
