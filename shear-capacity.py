import csv

class StructuralSection:

    PI=3.1416

    def __init__(self, tag,l_w,h_w,H_w,phi_t,num_bars,s):
        self.tag = tag
        self.wall_length = l_w
        self.wall_height = h_w
        self.total_wall_height = H_w
        self.phi_t=phi_t
        self.num_bars=num_bars
        self.spacing=s
        self.section_area = self.calculate_section_area()
        self.moment_of_inertia = self.calculate_moment_of_inertia()
        self.Hw_lw_ratio = self.calculate_Hw_lw_ratio()
        self.bar_area=self.calculate_bar_area()
        self.reinforcement_area=self.calculate_reinforcement_area()
        self.rho=self.calculate_rho()
        self.alpha_c=self.calculate_alpha_c()
    
    def calculate_section_area(self):
        return self.wall_length * self.wall_height

    def calculate_moment_of_inertia(self):
        return (self.wall_length * self.wall_height**3) / 12

    def calculate_Hw_lw_ratio(self):
        return self.total_wall_height / self.wall_length
    
    def calculate_bar_area(self):
        return self.PI*(self.phi_t/2)**2 
    
    def calculate_reinforcement_area(self):
        return self.bar_area*self.num_bars 
    
    def calculate_rho(self):
        return self.reinforcement_area / (self.spacing*self.wall_height)
    
    def calculate_alpha_c(self):
        if self.Hw_lw_ratio<=1.5:
            alpha_c=0.25
        elif self.Hw_lw_ratio>=2.0:
            alpha_c=0.17
        else:
            alpha_c=0.25-((self.Hw_lw_ratio-1.5)*(0.08/0.5))

        return alpha_c

class Material:
    def __init__(self,f_c,f_y,f_ce,f_ye,lambda_c=1.0):
        self.f_c=f_c
        self.f_y=f_y
        self.f_ce=f_ce
        self.f_ye=f_ye
        self.lambda_c=lambda_c
        self.concrete_overstrength=f_c/f_ce
        self.steel_overstrength=f_y/f_ye
        self.total_overstrength=self.concrete_overstrength*self.steel_overstrength

class ShearCalculator:

    PHI_S = 0.6

    def __init__(self, section, material):

        self.section = section
        self.material = material
        self.Vn_18_10 = self.calculate_Vn_18_10()
        self.phi_Vn_18_10=  self.calculate_phi_Vn_18_10()
        self.phi_Annex_A= self.calculate_phi_Annex_A()
        self.Vn_Annex_A= self.calculate_Vn_Annex_A()
        self.phi_Vn_Annex_A = self.calculate_phi_Vn_Annex_A()

    def calculate_Vn_18_10(self):
        Vn=self.section.section_area * (0.083*self.section.alpha_c*self.material.lambda_c*self.material.f_c**0.5 + (self.section.rho * self.material.f_y))
        return Vn
    
    def calculate_phi_Vn_18_10(self):
        return self.PHI_S * self.Vn_18_10
    
    def calculate_Vn_Annex_A(self):
        Vn=1.5*self.section.section_area * (0.17*self.section.alpha_c*self.material.lambda_c*self.material.f_c**0.5 + (self.section.rho * self.material.f_ye))
        return Vn
    
    def calculate_phi_Annex_A(self):
        return 0.9*self.material.total_overstrength
    
    def calculate_phi_Vn_Annex_A(self):
        return self.phi_Annex_A * self.Vn_Annex_A


def read_inputs_from_csv(file_path):
    inputs = []
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as file:  # Use utf-8-sig to handle BOM
            reader = csv.DictReader(file)
            # Print column names for debugging
            # print("Columns in CSV file:", reader.fieldnames)
            # Convert column names to lowercase and strip spaces
            reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
            for row in reader:
                # Convert numeric values to float
                row['tag'] = str(row['tag'])
                row['wall_length'] = float(row['l_w'])
                row['wall_height'] = float(row['h_w'])
                row['f_c'] = float(row['f_c'])
                row['f_y'] = float(row['f_y'])
                row['f_ce'] = float(row['f_ce'])
                row['f_ye'] = float(row['f_ye'])
                row['total_wall_height'] = float(row['h_tw'])
                row['phi_t'] = float(row['phi_t'])
                row['num_bars'] = float(row['num_bars'])
                row['s'] = float(row['s'])
                inputs.append(row)
        print("CSV file read successfully!")
        return inputs
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []
    except KeyError as e:
        print(f"Error: Missing required column in CSV file - {e}")
        return []
    except ValueError as e:
        print(f"Error: Invalid data format in CSV file - {e}")
        return []

def save_list_to_csv(data, file_path):
    """
    Saves a list of data to a CSV file.

    Args:
        data (list): A list of lists, where each inner list represents a row.
        file_path (str): Path to the output CSV file.
    """
    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(data)  # Write all rows to the CSV file
        print(f"Data saved to {file_path} successfully!")
    except Exception as e:
        print(f"Error: {e}")



# Main Program
if __name__ == "__main__":
    from pathlib import Path
    path = Path(__file__).parent
    input_path = path/ "inputs.csv"
    output_path = path / "outputs.csv"

    inputs = read_inputs_from_csv(input_path)

    sections_tag=[]
    shear_capacities_18=[]
    shear_capacities_A=[]
    if inputs:
        for input_data in inputs:
            # Create instances
            section = StructuralSection(input_data["tag"],
                                        input_data['wall_length'],
                                        input_data['wall_height'],
                                        input_data["total_wall_height"],
                                        input_data['phi_t'],
                                        input_data['num_bars'],
                                        input_data['s'],
                                        )
            material = Material(
                input_data['f_c'],
                input_data['f_y'],
                input_data['f_ce'],
                input_data['f_ye'],
            )
            shear=ShearCalculator(section, material)
            shear_capacities_18.append(shear.phi_Vn_18_10)
            shear_capacities_A.append(shear.phi_Vn_Annex_A)
            sections_tag.append(section.tag)
    
    data=[sections_tag,shear_capacities_18,shear_capacities_A]
    save_list_to_csv(data,output_path)
