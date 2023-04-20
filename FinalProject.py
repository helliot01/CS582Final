import numpy             as np
import matplotlib.pyplot as plt
from stl import mesh
from hilbert import decode

from mpl_toolkits import mplot3d
from matplotlib import pyplot


num_dims = 2
def generate_curve(num_bits,height):
    # The maximum Hilbert integer.
    max_h = 2**(num_bits*num_dims)

    # Generate a sequence of Hilbert integers.
    hilberts = np.arange(max_h)
    # Compute the 2-dimensional locations.
    locs = decode(hilberts, num_dims, num_bits)
    vertices = []
    for entry in locs: 
        vertices.append([entry[0],entry[1], height])
    return vertices

def draw_curve(locs, ax, num_bits):
    # Draw
    ax.plot(locs[:,0], locs[:,1], '.-')
    ax.set_aspect('equal')
    ax.set_title('%d bits per dimension' % (num_bits))
    ax.set_xlabel('dim 1')
    ax.set_ylabel('dim 2')


def generate_basic_mesh():
    v0 = generate_curve(2,0)
    v1 = generate_curve(2,1)
    slices = 2
    num_vertices = len(v0)
    vertices = np.asarray(v0 + v1)

    faces = triangulate(slices, num_vertices)

    cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            cube.vectors[i][j] = vertices[f[j],:]
    cube.save('cube.stl')

def triangulate(slices, num_vertices):
    f = []
    #for every slice, take i of slice n, slice i of n+1, slice i+1 of n. slice i,i+1 of n+, slice i+1 of n
    for x in range(slices-1):
        i=0
        while(i<num_vertices-1):
            curr_ind = x*num_vertices + i
            above_ind = (x+1)*num_vertices + i
            f.append([curr_ind, curr_ind+1, above_ind])
            f.append([above_ind, above_ind+1, curr_ind+1])
            i+=1
    faces = np.asarray(f)
    return faces

def plot_stl(your_mesh):
    figure = pyplot.figure()
    axes = figure.add_subplot(projection='3d')

    axes.add_collection3d(mplot3d.art3d.Poly3DCollection(your_mesh.vectors))

    # Auto scale to the mesh size
    scale = your_mesh.points.flatten()
    axes.auto_scale_xyz(scale, scale, scale)

    # Show the plot to the screen
    pyplot.show()



generate_basic_mesh()
# Load the STL files and plot
your_mesh = mesh.Mesh.from_file('cube.stl')
plot_stl(your_mesh)


