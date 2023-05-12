import numpy             as np
import matplotlib.pyplot as plt
from stl import mesh
from hilbert import decode

import argparse

from mpl_toolkits import mplot3d
from matplotlib import pyplot
import cubic_hermit as ch


FD = ch.TCubicHermiteSpline.FINITE_DIFF
GRAD = ch.TCubicHermiteSpline.GRAD
TRI_VERT = 3
num_dims = 2

# This script is the main file for both hilbert curve generation and interpolation
# To use this file in terminal here are 2 sample command one of generation and one for interpolaiton
# (make sure that  --layer are the same in both command)

#python3 FinalProject.py --mode=create --order=2 --layer=2

#python3 FinalProject.py --mode=interpolation --resolution=10 --layer=2 --Ipath=morphed_cube.obj

# To show the output of this file while using blender,e.g. activate blender in MacOS :
# /Applications/Blender.app/Contents/MacOS/Blender

def parse_arg():
    parser = argparse.ArgumentParser(description='Train a detector')
    parser.add_argument('--mode',
                        type=str,
                        default='create',
                        help='create for control points , interpolation for interpolation')
    parser.add_argument('--order',
                        type=int,
                        default= None,
                        help='num of hilbert curve bits')
    parser.add_argument('--layers',
                        type=int,
                        default= None,
                        help='num of layers')
    parser.add_argument('--control_stl',
                        type=str,
                        default= None,
                        help='control stl for interpolation input')
    parser.add_argument('--resolution',
                        type=int,
                        default= None,
                        help='interpolation resolution')

    parser.add_argument(
        '--Ipath',
        default=None,
        help='input path')

    parser.add_argument(
        '--Opath',
        default=None,
        help='output path')

    args = parser.parse_args()

    return args



def generate_curve(num_bits,height):
    max_h = 2**(num_bits*num_dims)

    # Generate a sequence of Hilbert integers.
    hilberts = np.arange(max_h)
    # Compute the 2-dimensional locations.
    locs = decode(hilberts, num_dims, num_bits)

    quarter = int(len(locs)/4)
    middle = locs[quarter:(3*quarter)]

    locs = np.asarray(locs)
    idx = np.unravel_index(np.argmax(locs), locs.shape)

    locs = np.asarray(middle)
    flipped = locs.copy()
    for r in range(len(flipped)):
        flipped[r][1] = (flipped[r][1] * -1) + locs[idx]
    firstq = np.asarray(flipped[:quarter])
    lastq = np.asarray(flipped[quarter:])
    locs = np.concatenate((flipped,middle[::-1]))
    # print(locs[0], locs[-1])

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

def triangulation(slices, num_vertices):
    return [(i, i+1, i+num_vertices) for i in range(1, num_vertices * slices, num_vertices)]



# function to generate and stack Hilbert curve Control points 
# currently we only stack the same hilbert curve on other 
def generate_basic_mesh(order : int,slices :int, path = 'control_cube.obj'):
        v0 = generate_curve(order,0) ##generate hilbert curves here for each slice
        vertices = np.asarray(v0)
        for i in range(1,slices):
            vertices = np.concatenate((vertices, np.asarray(generate_curve(order,i))), axis=0)
        vertices[:,0] = vertices[:,0] - 1 
        print('np',vertices)
        print('np',vertices.shape)
        num_vertices = int(vertices.shape[0] / slices)

        faces = triangulate(slices, num_vertices)
        faces = faces + 1
        print('faces',faces)
        #faces = triangulation(slices, num_vertices)
        with open(path, 'w') as file:
            for vertex in vertices:
                file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")

            # Write faces
            for face in faces:
                file.write(f"f {face[0]} {face[1]} {face[2]}\n") 
           

        #cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        #cube.vertices = vertices
        #for i, f in enumerate(faces):
        #    for j in range(TRI_VERT):
        #        cube.vectors[i][j] = vertices[f[j],:]
        #cube.save(path)

#function to interpolate layers of hilbert curve by creating a spline representation per layer
def interpolate_basic_mesh(vertices, resolution, slices, path = 'interpolated_cube.stl'):
    int_vertices = np.zeros(shape=(resolution * vertices.shape[0],3))#solution
    num_vertices = int(vertices.shape[0] / slices) #number of vertices per layer before interpolation

    for i in range(slices):
        layer = vertices[(i*num_vertices) : (i+1)*num_vertices]
        chs_finite = ch.TCubicHermiteSpline()
        vertex_time = np.arange(layer.shape[0]) # integer time steps per control point
        spaced_time = np.linspace(0,layer.shape[0] - 1 ,resolution * layer.shape[0])
        int_layer = interpolate(chs_finite, vertex_time, spaced_time, layer)
        print(int_layer.shape)
        int_vertices[i*num_vertices * resolution: (i+1)* num_vertices *resolution ,:] = int_layer
        #int_vertices = np.concatenate((int_vertices , int_layer),axis=0)


    print(int_vertices.shape)
    #vertices = vertices.squeeze(axis=0)

    int_num_vertices = int(int_vertices.shape[0] / slices)
    
    #print('int vertices', vertices) 
    faces = triangulate(slices, int_num_vertices)

    cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(TRI_VERT):
            cube.vectors[i][j] = int_vertices[f[j],:]
    cube.save(path)

# interpolation that for the time being only applicable in first 2 (x,y) directions
def interpolate(chs_finite, vertex_time, spaced_time, vertices):
    v1_np = np.array(vertices)
    t_v1 = np.array([( t, X) for t, X in zip(vertex_time, v1_np) ],dtype= object)
    chs_finite.Initialize(t_v1,tan_method=FD, end_tan = GRAD)

    int_v1 = np.zeros( shape=[spaced_time.size,3],dtype=float)

    for idx in range(spaced_time.size):
        int_v1[idx] = chs_finite.Evaluate(spaced_time[idx])
    return int_v1

def triangulate(slices, num_vertices):
    f = []
    #for every slice, take i of slice n, slice i of n+1, slice i+1 of n. slice i,i+1 of n+, slice i+1 of n
    for x in range(slices-1):
        i=0
        while(i<num_vertices-1):
            curr_ind = x*num_vertices + i
            above_ind = (x+1)*num_vertices + i
            f.append([curr_ind, above_ind, curr_ind+1])
            f.append([above_ind, above_ind+1, curr_ind+1])
            i+=1
        f.append([x*num_vertices,(x+1)*num_vertices, (x+1)*num_vertices-1])
        f.append([(x+1)*num_vertices, (x+1)*num_vertices-1, (x+1)*num_vertices+i])
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

def main():
    args = parse_arg()
    print('parsed', args)
    if args.mode == 'create':
        if(args.Opath != None):
            generate_basic_mesh(args.order, args.layers, args.Opath)
        else:
            generate_basic_mesh(args.order,args.layers)
    elif args.mode == 'interpolation':
        if(args.Ipath != None):
            print('interpolating')
            #mesh_stl = .Mesh.from_file(args.Ipath)
            #mesh_stl = mesh.Mesh.from_file(args.Ipath)
            vertices = []
            with open(args.Ipath, 'r') as f:
                for line in f:
                    if line.startswith('v'):
                        #print('line',line)
                        vertices.append(line.split()[1:])
                        
            mesh_obj = np.array(vertices, dtype=float)
            print('imported_mesh_vertices', mesh_obj)
            if(args.Opath!= None):
                interpolate_basic_mesh(mesh_obj, args.resolution, args.layers, args.Opath)
            else:
                interpolate_basic_mesh(mesh_obj , args.resolution, args.layers)
    
main()
#generate_basic_mesh(2)
# Load the STL files and plot
#your_mesh = mesh.Mesh.from_file('control_cube.stl')
#plot_stl(your_mesh)


