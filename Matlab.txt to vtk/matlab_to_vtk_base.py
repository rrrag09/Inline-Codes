import numpy as np
import os

# Read the file
filename = "Piston_Gap_Pressure.txt"

with open(filename, 'r') as f:
    lines = f.readlines()

# Parse data
phi_sections = []
current_phi = None
current_data = []

for line in lines:
    line = line.strip()
    if line.startswith('%PHI'):
        if current_phi is not None:
            phi_sections.append((current_phi, np.array(current_data)))
            current_data = []
        # Extract phi value
        current_phi = float(line.split(':')[1].strip().split()[0])
    elif line.startswith('%') or line == '':
        continue
    else:
        # Data line
        values = [float(x) for x in line.split()]
        current_data.append(values)

# Add last section
if current_phi is not None and current_data:
    phi_sections.append((current_phi, np.array(current_data)))

# Filter to keep only the last 360 degrees
if len(phi_sections) > 0:
    # The number of files equals number of phi values per revolution
    files_per_revolution = len(phi_sections) // int(len(phi_sections) / 360) if len(phi_sections) > 360 else len(phi_sections)
    
    # For simplicity, assume 360 files per revolution (one per degree)
    num_per_revolution = 360
    
    # Calculate starting index for last revolution
    last_revolution_start_idx = len(phi_sections) - num_per_revolution
    
    # Filter to keep only sections from last revolution
    last_revolution_sections = phi_sections[last_revolution_start_idx:]
    
    total_revolutions = len(phi_sections) / num_per_revolution
    actual_start_degree = last_revolution_start_idx
    
    print(f"Total files: {len(phi_sections)}")
    print(f"Total revolutions: {total_revolutions:.1f}")
    print(f"Last revolution starts at index: {last_revolution_start_idx} (degree {actual_start_degree})")
    print(f"Processing {len(last_revolution_sections)} files from last revolution\n")
else:
    last_revolution_sections = phi_sections

# Create output folder
output_folder = "piston_pressure_phi"
os.makedirs(output_folder, exist_ok=True)

# Store filenames for PVD creation
vtk_files_list = []

# Create VTK files
for idx, (phi, data) in enumerate(last_revolution_sections):
    N, M = data.shape  # N = circumferential, M = radial

    # Calculate actual degree based on position in the original list
    actual_degree = len(phi_sections) - len(last_revolution_sections) + idx

    vtk_filename = f"piston_pressure_phi.{int(actual_degree)}.vtk"
    vtk_filepath = os.path.join(output_folder, vtk_filename)

    with open(vtk_filepath, 'w') as vtk:
        vtk.write("# vtk DataFile Version 2.0\n")
        vtk.write(f"Piston Gap Pressure at {actual_degree:.1f} deg\n")
        vtk.write("ASCII\n")
        vtk.write("DATASET STRUCTURED_POINTS\n")
        vtk.write(f"DIMENSIONS {M} {N} 1\n")
        vtk.write("ORIGIN 0 0 0\n")
        vtk.write("SPACING 1 1 1\n")
        vtk.write(f"POINT_DATA {N * M}\n")
        vtk.write("SCALARS Pressure_bar double 1\n")
        vtk.write("LOOKUP_TABLE default\n")

        for i in range(N):
            for j in range(M):
                vtk.write(f"{data[i, j]}\n")

    vtk_files_list.append((actual_degree, vtk_filename))
    print(f"Created: {vtk_filename}")

# Create PVD file for time series animation
pvd_filename = "piston_pressure_animation.pvd"
pvd_filepath = os.path.join(output_folder, pvd_filename)

with open(pvd_filepath, 'w') as pvd:
    pvd.write('<?xml version="1.0"?>\n')
    pvd.write('<VTKFile type="Collection" version="0.1">\n')
    pvd.write('  <Collection>\n')
    
    for degree, vtk_file in vtk_files_list:
        pvd.write(f'    <DataSet timestep="{degree}" group="" part="0" file="{vtk_file}"/>\n')
    
    pvd.write('  </Collection>\n')
    pvd.write('</VTKFile>\n')

print(f"\nTotal files created: {len(last_revolution_sections)}")
print(f"Files saved in folder: {output_folder}")
print(f"\nAnimation file created: {pvd_filename}")
print(f"Load '{pvd_filename}' in ParaView and press Play to see the animation!")