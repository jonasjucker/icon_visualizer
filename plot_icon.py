import Ngl,Nio, numpy
import sys
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-df','--data-file',  dest = 'data',\
                    help='NetCDF with Icon data') 

parser.add_argument('-gf','--grid-file',  dest = 'grid',\
                    help='corresponding icon grid to fields to plot') 

parser.add_argument('-f', '--field',  dest = 'var',\
                    default = 'topography_c',\
                    help = 'field to plot') 

parser.add_argument('--corners', '-c', dest = 'corner',\
                    default = [5.5,10.5,44.5,48.5],\
                    type = int,\
                    nargs = 4,\
                    help = 'corners of domain to plot: MinLon MaxLon MinLat MaxLat')

parser.add_argument('--global_plot','-gp', action='store_true',\
                    help = 'plot an additional global plot')

parser.add_argument('--grid_only','-go', action='store_true',\
                    help = 'plot the icon grid only and exit')

args = parser.parse_args()

gridfile = Nio.open_file(args.grid)
vlon = numpy.rad2deg( gridfile.variables["vlon"][:] )
vlat = numpy.rad2deg( gridfile.variables["vlat"][:] )

edge_vertices = gridfile.variables["edge_vertices"][:]

wks = Ngl.open_wks("pdf","map")


if args.grid_only:

    print('Plot Grid only')

    config = Ngl.Resources()
    config.nglFrame             = False
    config.nglDraw              = False
    config.mpProjection          = "Orthographic"
    config.mpLimitMode           = "LatLon"
    config.mpMinLonF             = 0
    config.mpMaxLonF             = 18
    config.mpMinLatF             = 43
    config.mpMaxLatF             = 50

    map = Ngl.map(wks,config)

    ecx = numpy.ravel( vlon[ edge_vertices-1 ], order='F' )
    ecy = numpy.ravel( vlat[ edge_vertices-1 ], order='F' )

    lines_cfg = Ngl.Resources()
    lines_cfg.gsSegments = numpy.arange(0, edge_vertices.size, 2)
    poly = Ngl.add_polyline(wks, map, ecx, ecy, lines_cfg)

    Ngl.draw(map)
    Ngl.frame(wks)
    Ngl.end()
    sys.exit()


# regular plot
print('Plot regular')
datafile = Nio.open_file(args.data)
field = datafile.variables[args.var]

clon  = numpy.rad2deg( gridfile.variables["clon"][:] )
clat  = numpy.rad2deg( gridfile.variables["clat"][:] )
clonv  = numpy.rad2deg( gridfile.variables["clon_vertices"][:] )
clatv  = numpy.rad2deg( gridfile.variables["clat_vertices"][:] )

config1 = Ngl.Resources()
config1.mpProjection          = "CylindricalEquidistant"
config1.mpLimitMode           = "LatLon"
config1.mpMinLonF             = args.corner[0]
config1.mpMaxLonF             = args.corner[1]
config1.mpMinLatF             = args.corner[2]
config1.mpMaxLatF             = args.corner[3]
config1.cnFillOn              = True
config1.cnLinesOn             = False
config1.cnLineLabelsOn        = False
config1.sfXArray              = clon
config1.sfYArray              = clat

# make icon-triangles visible
clon_vertices                 = clonv
clat_vertices                 = clatv
config1.sfXCellBounds         = clon_vertices
config1.sfYCellBounds         = clat_vertices
config1.cnFillMode            = "CellFill"

map = Ngl.contour_map(wks,field,config1)

if args.global_plot:
    print('Plot global')

    config2 = Ngl.Resources()
    config2.mpProjection          = "Orthographic"
    config2.mpLimitMode           = "LatLon"
    config2.mpMinLonF             = 0
    config2.mpMaxLonF             = 18
    config2.mpMinLatF             = 43
    config2.mpMaxLatF             = 50
    config2.cnFillOn              = True
    config2.cnLinesOn             = False
    config2.cnLineLabelsOn        = False
    config2.sfXArray              = clon
    config2.sfYArray              = clat

    # make icon-triangles visible
    clon_vertices                 = clonv
    clat_vertices                 = clatv
    config2.sfXCellBounds         = clon_vertices
    config2.sfYCellBounds         = clat_vertices
    config2.cnFillMode            = "CellFill"

    map = Ngl.contour_map(wks,field,config2)

Ngl.end()
