import vtk
from vtk.util import numpy_support
import numpy as np
from fury import actor, window, ui
from fury.utils import numpy_to_vtk_points, numpy_to_vtk_colors, set_polydata_colors
from fury.utils import set_input, rotate, set_polydata_vertices
from fury.utils import get_actor_from_polydata, set_polydata_triangles



def square(scale=1):
    my_polydata = vtk.vtkPolyData()

    my_vertices = np.array([[0.0, 0.0, 0.0],
                            [0.0, 1.0, 0.0],
                            [1.0, 1.0, 0.0],
                            [1.0, 0.0, 0.0]])

    my_vertices -= np.array([0.5, 0.5, 0])

    my_vertices = scale * my_vertices

    my_triangles = np.array([[0, 1, 2],
                             [2, 3, 0]], dtype='i8')

    set_polydata_vertices(my_polydata, my_vertices)
    set_polydata_triangles(my_polydata, my_triangles)

    return get_actor_from_polydata(my_polydata)


def cube():
    my_polydata = vtk.vtkPolyData()

    my_vertices = np.array([[0.0, 0.0, 0.0],
                            [0.0, 0.0, 1.0],
                            [0.0, 1.0, 0.0],
                            [0.0, 1.0, 1.0],
                            [1.0, 0.0, 0.0],
                            [1.0, 0.0, 1.0],
                            [1.0, 1.0, 0.0],
                            [1.0, 1.0, 1.0]])

    my_vertices -= 0.5

    my_triangles = np.array([[0, 6, 4],
                            [0, 2, 6],
                            [0, 3, 2],
                            [0, 1, 3],
                            [2, 7, 6],
                            [2, 3, 7],
                            [4, 6, 7],
                            [4, 7, 5],
                            [0, 4, 5],
                            [0, 5, 1],
                            [1, 5, 7],
                            [1, 7, 3]], dtype='i8')

    set_polydata_vertices(my_polydata, my_vertices)
    set_polydata_triangles(my_polydata, my_triangles)
    return get_actor_from_polydata(my_polydata)

scene = window.Scene()
# scene.add(actor.axes())
# scene.background((1, 1, 1))
showm = window.ShowManager(scene, size=(1920, 1080),
                           order_transparent=True,
                           interactor_style='custom')

obj = 'cube'

if obj == 'square':

    sq = square(3)
    sq.GetProperty().BackfaceCullingOff()
    scene.add(sq)
    mapper = sq.GetMapper()

if obj == 'cube':

    # rec.SetPosition(100, 0, 0)
    cu = cube()
    cu.GetProperty().BackfaceCullingOff()
    scene.add(cu)
    scene.background((1, 1, 1))
    # window.show(scene)
    mapper = cu.GetMapper()


import itertools
counter = itertools.count(start=1)

global timer

timer = 0

def timer_callback(obj, event):

    global timer
    timer += 1.0
    # print(timer)
    showm.render()
    # scene.azimuth(10)


@window.vtk.calldata_type(window.vtk.VTK_OBJECT)
def vtk_shader_callback(caller, event, calldata=None):
    program = calldata
    global timer
    if program is not None:
        try:
            program.SetUniformf("time", timer)
        except ValueError:
            pass


mapper.AddObserver(window.vtk.vtkCommand.UpdateShaderEvent,
                   vtk_shader_callback)


mapper.AddShaderReplacement(
    vtk.vtkShader.Vertex,
    "//VTK::Normal::Dec",
    True,
    "//VTK::Normal::Dec\n"
    "out vec4 myVertexMC;\n",
    False
  )
mapper.AddShaderReplacement(
    vtk.vtkShader.Vertex,
    "//VTK::Normal::Impl",
    True,
    "//VTK::Normal::Impl\n"
    "  myVertexMC = vertexMC;\n",
    False
  )

# mapper.AddShaderReplacement(
#     vtk.vtkShader.Fragment,
#     '//VTK::Light::Dec',
#     True,
#     '''
#     //VTK::Light::Dec
#     uniform float time;
#     ''',
#     False
# )

mapper.AddShaderReplacement(
      vtk.vtkShader.Fragment,
      "//VTK::Normal::Dec",
      True,
      "//VTK::Normal::Dec\n"
      "varying vec4 myVertexMC;\n"
      "uniform float time;\n",
      False
  )
mapper.AddShaderReplacement(
    vtk.vtkShader.Fragment,
    '//VTK::Light::Impl',
    True,
    '''
    //VTK::Light::Impl
    if (myVertexMC == vec4(0.5, 0.5, 0.5, 1.0))
        {fragOutput0 = vec4(1., 1., 1., 1.); return;}
    vec3 rColor = vec3(.9, .0, .3);
    vec3 gColor = vec3(.0, .9, .3);
    vec3 bColor = vec3(.0, .3, .9);
    vec3 yColor = vec3(.9, .9, .3);

    float tm = .2; // speed
    float vcm = 5;

    float a = sin(myVertexMC.y * vcm - time * tm) / 2.;
    float b = cos(myVertexMC.y * vcm - time * tm) / 2.;
    float c = sin(myVertexMC.y * vcm - time * tm + 3.14) / 2.;
    float d = cos(myVertexMC.y * vcm - time * tm + 3.14) / 2.;

    float div = 0.01; // default 0.01

    float e = div / abs(myVertexMC.x + a);
    float f = div / abs(myVertexMC.x + b);
    float g = div / abs(myVertexMC.x + c);
    float h = div / abs(myVertexMC.x + d);

    vec3 destColor = rColor * e + gColor * f + bColor * g + yColor * h;
    fragOutput0 = vec4(destColor, 1.);
    //fragOutput0 = vec4(1 - myVertexMC.x, 1 - myVertexMC.y, 0, 1.);
    //fragOutput0 = vec4(myVertexMC.x, 0, 0, 1.);
    //vec2 p = vertexVCVSOutput.xy; //- vec2(1.5,0.5);
    vec2 p = myVertexMC.xy;
    //fragOutput0 = 0.5 * (vec4(0, 0.5, 0., 1.) + fragOutput0);
    //fragOutput0 =  fragOutput0);


    if (length(p - vec2(0, 0)) < 0.2) {
        fragOutput0 = vec4(1, 0., 0., .5);

    }

    if (length(p - vec2(1, 1)) < 0.2) {
        fragOutput0 = vec4(1, 0., 0., .5);
    }

    ''',
    False
)

showm.initialize()
showm.add_timer_callback(True, 100, timer_callback)

showm.initialize()
showm.start()