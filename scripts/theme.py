import os
import shutil
import colorsys  # colorsys.hls_to_rgb(h, l, s)

from .utils import (
    replace_keywords,    # replace keywords in file
    copy_files,          # copy files from source to destination
    destination_return,  # copied/modified theme location
    generate_file)       # combine files from folder to one file


class Theme:
    def __init__(self, theme_type, colors_json, theme_folder, destination_folder, temp_folder, is_filled=False):
        """
        Initialize Theme class
        :param colors_json: location of a json file with colors
        :param theme_type: theme type (gnome-shell, gtk, etc.)
        :param theme_folder: raw theme location
        :param destination_folder: folder where themes will be installed
        :param temp_folder: folder where files will be collected
        :param is_filled: if True, theme will be filled
        """

        self.colors = colors_json
        self.temp_folder = f"{temp_folder}/{theme_type}"
        self.theme_folder = theme_folder
        self.theme_type = theme_type
        self.destination_folder = destination_folder
        self.main_styles = f"{self.temp_folder}/{theme_type}.css"

        # move files to temp folder
        copy_files(self.theme_folder, self.temp_folder)
        generate_file(f"{self.theme_folder}_css/", self.main_styles)

        # if theme is filled
        
        """
        if is_filled:
            for apply_file in os.listdir(f"{self.temp_folder}/"):
                replace_keywords(f"{self.temp_folder}/{apply_file}",
                                 ("BUTTON-COLOR", "ACCENT-FILLED-COLOR"),
                                 ("BUTTON_HOVER", "ACCENT-FILLED_HOVER"),
                                 ("BUTTON_INSENSITIVE", "ACCENT-FILLED_INSENSITIVE"),
                                 ("BUTTON-TEXT-COLOR", "TEXT-BLACK-COLOR"),
                                 ("BUTTON-TEXT_SECONDARY", "TEXT-BLACK_SECONDARY"))
        """

    def __add__(self, other):
        """
        Add to main styles another styles
        :param other: styles to add
        :return: new Theme object
        """

        with open(self.main_styles, 'a') as main_styles:
            main_styles.write('\n' + other)
        return self

    def __mul__(self, other):
        """
        Copy files to temp folder
        :param other: file or folder
        :return: new Theme object
        """

        if os.path.isfile(other):
            shutil.copy(other, self.temp_folder)
        else:
            shutil.copytree(other, self.temp_folder)

        return self

    def __del__(self):
        # delete temp folder
        os.system(f"rm -r {self.temp_folder}")
        
    def adjust_lightness(self, hexColor, factor=1.1):
        r, g, b = float(int(hexColor[1:3], 16)), float(int(hexColor[3:5], 16)), float(int(hexColor[5:], 16))
        print(r, g, b)
        h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        l = max(min(l * factor, 1.0), 0.0)
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        return "#%02x%02x%02x" % (r,g,b)

    def __apply_colors(self, destination, apply_file, flavor, accent):
        """
        Install accent colors from colors.json to different file
        :param hue
        :param destination: file directory
        :param apply_file: file name
        :param sat: color saturation (optional)
        """
        colors = self.colors["@" + flavor]
        # list of (keyword, replaced value)
        replaced_colors = list()
        
        replaced_colors.append(("@accent-color", colors["@" + accent]))
        replaced_colors.append(("@accent-color-hover", self.adjust_lightness(colors["@"+ accent])))
        
        for keyword in colors:
            replaced_colors.append((keyword, colors[keyword]))

        # replace colors
        replace_keywords(os.path.expanduser(f"{destination}/{apply_file}"), *replaced_colors)

    def __apply_theme(self, source, destination, flavor, accent):
        """
        Apply theme to all files in directory
        :param hue
        :param source
        :param destination: file directory
        :param sat: color saturation (optional)
        """

        for apply_file in os.listdir(f"{source}/"):
            self.__apply_colors(destination, apply_file, flavor, accent)

    def install(self, flavor, accent, destination=None):
        """
        Copy files and generate theme with different accent color
        :param hue
        :param name: theme name
        :param sat: color saturation (optional)
        :param destination: folder where theme will be installed
        """
        name = flavor + "-" + accent
        is_dest = bool(destination)

        print(f"Creating {name} theme...", end=" ")

        try:
            if not is_dest:
                destination = destination_return(self.destination_folder, name, self.theme_type)

            copy_files(self.temp_folder + '/', destination)
            self.__apply_theme(self.temp_folder, destination, flavor, accent)

        except Exception as err:
            print("\nError: " + str(err))

        else:
            print("Done.")

    def add_to_start(self, content):
        """
        Add content to the start of main styles
        :param content: content to add
        """

        with open(self.main_styles, 'r') as main_styles:
            main_content = main_styles.read()

        with open(self.main_styles, 'w') as main_styles:
            main_styles.write(content + '\n' + main_content)
