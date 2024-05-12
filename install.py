# This file installs Marble shell theme for GNOME DE
# Copyright (C) 2023  Vladyslav Hroshev

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import json       # working with json files
import argparse   # command-line options
import shutil
import textwrap   # example text in argparse

from scripts import config     # folder and files definitions

from scripts.utils import (
    remove_files,  # delete already installed Marble theme
    hex_to_rgba)   # convert HEX to RGBA

from scripts.theme import Theme
from scripts.gdm import GlobalTheme


def parse_args():
    """
    Parse command-line arguments
    :return: parsed arguments
    """

    # script description
    parser = argparse.ArgumentParser(prog="python install.py",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent('''
                    Examples:
                      -a                            all accent colors, all flavors
                      --all                         all accent colors, dark mode
                      --purple                      purple accent color, light mode
                      --hue 150 --name coldgreen    custom coldgreen accent color, light & dark mode
                      --red --green                 red, green accent colors
                    '''))

    # Default arguments
    parser.add_argument('-r', '--remove', action='store_true', help='remove all "Marble" themes')

    accentColors = parser.add_argument_group('Accent Colors')
    accentColors.add_argument('-a', '--all', action='store_true', help='all available accent colors')
    accentColors.add_argument('--rosewater', action='store_true', help='Rosewater Accent Color')
    accentColors.add_argument('--flamingo', action='store_true', help='Flamingo Accent Color')
    accentColors.add_argument('--pink', action='store_true', help='Pink Accent Color')
    accentColors.add_argument('--mauve', action='store_true', help='Mauve Accent Color')
    accentColors.add_argument('--red', action='store_true', help='Red Accent Color')
    accentColors.add_argument('--maroon', action='store_true', help='Maroon Accent Color')
    accentColors.add_argument('--peach', action='store_true', help='Peach Accent Color')
    accentColors.add_argument('--yellow', action='store_true', help='Yellow Accent Color')
    accentColors.add_argument('--green', action='store_true', help='Green Accent Color')
    accentColors.add_argument('--teal', action='store_true', help='Teal Accent Color')
    accentColors.add_argument('--sky', action='store_true', help='Sky Accent Color')
    accentColors.add_argument('--sapphire', action='store_true', help='Sapphire Accent Color')
    accentColors.add_argument('--blue', action='store_true', help='Blue Accent Color')
    accentColors.add_argument('--lavender', action='store_true', help='Lavender Accent Color')

    flavors = parser.add_argument_group('Flavors')
    flavors.add_argument('--latte', action='store_true', help='latte flavor')
    flavors.add_argument('--frappe', action='store_true', help='frappe flavor')
    flavors.add_argument('--macchiato', action='store_true', help='macchiato flavor')
    flavors.add_argument('--mocha', action='store_true', help='mocha flavor')

    gdm_theming = parser.add_argument_group('GDM theming')
    gdm_theming.add_argument('--gdm', action='store_true', help='install GDM theme. \
                                    Requires root privileges. You must specify a specific color.')

    panel_args = parser.add_argument_group('Panel tweaks')
    panel_args.add_argument('-Pds', '--panel_default_size', action='store_true', help='set default panel size')
    panel_args.add_argument('-Pnp', '--panel_no_pill', action='store_true', help='remove panel button background')

    overview_args = parser.add_argument_group('Overview tweaks')
    overview_args.add_argument('--launchpad', action='store_true', help='change Show Apps icon to MacOS Launchpad icon')

    return parser.parse_args()


def apply_tweaks(args, theme):
    """
    Apply theme tweaks
    :param args: parsed arguments
    :param theme: Theme object
    """

    if args.panel_default_size:
        with open(f"{config.tweaks_folder}/panel/def-size.css", "r") as f:
            theme += f.read()

    if args.panel_no_pill:
        with open(f"{config.tweaks_folder}/panel/no-pill.css", "r") as f:
            theme += f.read()

    if args.launchpad:
        with open(f"{config.tweaks_folder}/launchpad/launchpad.css", "r") as f:
            theme += f.read()

        theme *= f"{config.tweaks_folder}/launchpad/launchpad.png"


def install_theme(theme, flavor, accent, gdm=False):
    """
    Check if GDM and install theme
    :param theme: object to install
    :param hue: color hue
    :param theme_name: future theme name
    :param sat: color saturation
    :param gdm: if GDM theme
    """

    theme.install(flavor, accent)

def apply_colors(args, theme, colors, gdm=False):
    """
    Apply accent colors to the theme
    :param args: parsed arguments
    :param theme: Theme object
    :param colors: colors from colors.json
    :param gdm: if GDM theme
    """
    accents = ["rosewater", "flamingo", "pink", "mauve", "red", "maroon", "peach", "yellow", "green", "teal", "sky", "sapphire", "blue", "lavender"]
    flavors = ["latte", "frappe", "macchiato", "mocha"]
    argsSpecified = False  # check if any color arguments specified
    for flavor in flavors:
        if args.all or getattr(args, flavor):
            for accent in accents:
                if args.all or getattr(args, accent):
                    argsSpecified = True
                    install_theme(theme, flavor, accent,  gdm)
                    if gdm:
                        return

    if not argsSpecified:
        print('No accent/flavor arguments specified. Use -h or --help to see the available options.')


def global_theme(args, colors):
    """
    Apply GDM theme
    :param args: parsed arguments
    :param colors: colors from colors.json
    """

    gdm_theme = GlobalTheme(colors, f"{config.raw_theme_folder}/{config.gnome_folder}",
                            config.global_gnome_shell_theme, config.gnome_shell_gresource,
                            config.temp_folder, is_filled=args.filled)

    if args.remove:
        gdm_rm_status = gdm_theme.remove()
        if gdm_rm_status == 0:
            print("GDM theme removed successfully.")
        return 0

    try:
        apply_colors(args, gdm_theme, colors, gdm=True)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    else:
        print("\nGDM theme installed successfully.")
        print("You need to restart gdm.service to apply changes.")
        print("Run \"systemctl restart gdm.service\" to restart GDM.")


def local_theme(args, colors):
    """
    Apply local theme
    :param args: parsed arguments
    :param colors: colors from colors.json
    """

    if args.remove:
        remove_files()

    gnome_shell_theme = Theme("gnome-shell", colors, f"{config.raw_theme_folder}/{config.gnome_folder}",
                              config.themes_folder, config.temp_folder)

    apply_tweaks(args, gnome_shell_theme)
    apply_colors(args, gnome_shell_theme, colors)


def main():
    args = parse_args()

    colors = json.load(open(config.colors_json))

    if args.gdm:
        global_theme(args, colors)

    # if not GDM theme
    else:
        local_theme(args, colors)


if __name__ == "__main__":
    main()

    shutil.rmtree(config.temp_folder, ignore_errors=True)
