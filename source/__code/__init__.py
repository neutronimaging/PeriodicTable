import os

file_path = os.path.dirname(__file__)
parent_path = os.path.dirname(file_path)

ATTENUATION_FILE = os.path.join(parent_path, "Attenuation_coefficients_chemical_elements.xlsx")
