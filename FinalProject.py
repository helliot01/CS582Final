import numpy             as np
import matplotlib.pyplot as plt
from stl import mesh
from hilbert import decode

from mpl_toolkits import mplot3d
from matplotlib import pyplot
import cubic_hermit as ch


FD = ch.TCubicHermiteSpline.FINITE_DIFF
GRAD = ch.TCubicHermiteSpline.GRAD

num_dims = 2
def generate_curve(num_bits,height):
    # The maximum Hilbert integer.
    max_h = 2**(num_bits*num_dims)

    # Generate a sequence of Hilbert integers.
    hilberts = np.arange(max_h)

    # Compute the 2-dimensional locations.
    locs = decode(hilberts, num_dims, num_bits)
    print()
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


def generate_basic_mesh(order):
    v0 = generate_curve(order,0) ##generate hilbert curves here for each slice
    v1 = generate_curve(order,1)
    v2 = generate_curve(order,2)

    slices = 3
    vertices = np.asarray(v0 + v1 + v2) #append all slices to one list of vertices for the stl generation

    chs_finite = ch.TCubicHermiteSpline()
    vertex_time = np.arange(len(v0)) # integer time steps per control point
    spaced_time = np.linspace(0,len(v0) - 1 ,10 * len(v0)) # smaller time steps for evaluation K 2 - n-1

    int_v0 = interpolate(chs_finite, vertex_time, spaced_time, v0)
    int_v1 = interpolate(chs_finite, vertex_time, spaced_time, v1)
    int_v2 = interpolate(chs_finite, vertex_time, spaced_time, v2)

    assert int_v0.shape[0] == (int_v1).shape[0] == int_v2.shape[0]
    num_vertices = int_v0.shape[0]
    vertices = np.concatenate((int_v0,int_v1,int_v2),axis=0)
    
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

def interpolate(chs_finite, vertex_time, spaced_time, vertices):
    v1_np = np.array(vertices)
    t_v1 = np.array([( t, X) for t, X in zip(vertex_time, v1_np) ],dtype= object)
    chs_finite.Initialize(t_v1,tan_method=FD, end_tan = GRAD)

    int_v1 = np.zeros( shape=[spaced_time.size,3],dtype=float)

    for idx in range(spaced_time.size):
        int_v1[idx] = chs_finite.Evaluate(spaced_time[idx])
    return int_v1


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


