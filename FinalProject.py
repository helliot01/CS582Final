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


def generate_basic_mesh():
    v0 = generate_curve(3,0)
    v1 = generate_curve(3,1)
    chs_finite = ch.TCubicHermiteSpline()
    vertex_time = np.arange(len(v0)) # integer time steps per control point
    spaced_time = np.linspace(0,len(v0) - 1 ,10 * len(v0)) # smaller time steps for evaluation K 2 - n-1
    v0_np = np.array(v0)
    t_v0 = np.array([( t, X) for t, X in zip(vertex_time, v0_np) ],dtype= object)
    chs_finite.Initialize(t_v0,tan_method=FD, end_tan = GRAD) 
    #print('first', v0_np[0])
    int_v0 = np.zeros( shape=[spaced_time.size,3],dtype=float)
    print('v0 init ',int_v0)


    print(spaced_time) 
    for idx in range(spaced_time.size):
        #print('shape per i',chs_finite.Evaluate(spaced_time[idx]))
        int_v0[idx] = chs_finite.Evaluate(spaced_time[idx])
        #int_v0 = np.vstack((int_v0, chs_finite.Evaluate(spaced_time[idx]).reshape(1,3)) )
    print('layer0: \n',int_v0)
    print('layer0 shape: \n',int_v0.shape)

    chs_finite = ch.TCubicHermiteSpline()
    vertex_time = np.arange(len(v1)) # integer time steps per control point
    spaced_time = np.linspace(0,len(v1) - 1 ,10 * len(v1)) # smaller time steps for evaluation K 2 - n-1
    v1_np = np.array(v1)
    t_v1 = np.array([( t, X) for t, X in zip(vertex_time, v1_np) ],dtype= object)
    chs_finite.Initialize(t_v1,tan_method=FD, end_tan = GRAD) 

    int_v1 = np.zeros( shape=[spaced_time.size,3],dtype=float)

    print('v1 init ',int_v1)
    #print(spaced_time) 
    for idx in range(spaced_time.size):
        #print(chs_finite.Evaluate(spaced_time[idx]))
        int_v1[idx] = chs_finite.Evaluate(spaced_time[idx])
    #int_v0 = np.array([v0[-1]]);
    print('layer1: \n',int_v1)

    slices = 2
    #num_vertices = len(v0)
    #vertices = np.asarray(v0 + v1)
    assert int_v0.shape[0] == (int_v1).shape[0]
    print('layer shape', int_v0.shape)
    num_vertices = int_v0.shape[0]
    vertices = np.concatenate((int_v0,int_v1),axis=0)
    print('concatenated shape: ', vertices.shape)

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


