{
  inputs.nixpkgs.url = "github:NixOs/nixpkgs/nixos-25.05";
  inputs.poetry2nix.url = "github:nix-community/poetry2nix";
  outputs = {self, nixpkgs, poetry2nix}:
  let 
    system = "x86_64-linux";
    pkgs = import nixpkgs {inherit system;};
    lib = pkgs.lib;
    p2n = poetry2nix.lib.mkPoetry2Nix {inherit pkgs; };
    in 
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          poetry
          python311
          nodejs_24
          stdenv.cc.cc.lib 
          zstd
          # Qt6 and PyQt6 dependencies
          qt6.qtbase
          qt6.qttools
          # System libraries
          zlib
          libGL
          libGLU
          xorg.libX11
          xorg.libXext
          xorg.libXrender
          xorg.libXi
          xorg.libXfixes
          fontconfig
          freetype
          dbus
          glib
          # Additional runtime libraries
          libxkbcommon
          wayland
        ];
        shellHook = ''
          export LD_LIBRARY_PATH=${lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.zstd
            pkgs.zlib
            pkgs.libGL
            pkgs.libGLU
            pkgs.xorg.libX11
            pkgs.xorg.libXext
            pkgs.xorg.libXrender
            pkgs.xorg.libXi
            pkgs.xorg.libXfixes
            pkgs.fontconfig
            pkgs.freetype
            pkgs.dbus
            pkgs.glib
            pkgs.libxkbcommon
            pkgs.wayland
          ]}:$LD_LIBRARY_PATH
          export QT_QPA_PLATFORM_PLUGIN_PATH=${pkgs.qt6.qtbase}/lib/qt-6/plugins
          export QT_PLUGIN_PATH=${pkgs.qt6.qtbase}/lib/qt-6/plugins
          export QML2_IMPORT_PATH=${pkgs.qt6.qtbase}/lib/qt-6/qml
        '';
      };
    };
}
