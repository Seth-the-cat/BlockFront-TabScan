{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
    pname = "blockfront-tabscan-shell";
    buildInputs = [
        pkgs.python3
        pkgs.python3Packages.pip
        pkgs.python3Packages.pandas
        pkgs.python3Packages.opencv4
        pkgs.python3Packages.numpy
        pkgs.python3Packages.pytesseract
        pkgs.python3Packages.easyocr
        pkgs.python3Packages.Pillow
    ];

    shellHook = ''
        export PYTHONPATH="${toString ./.}:$PYTHONPATH"
    '';
}
