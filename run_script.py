import OpenPNM
from time import clock
start=clock()

#======================================================================
'''Initialize empty Network object'''
#======================================================================
pn = OpenPNM.Base.Network(loggername='PNM',loglevel=20)

#======================================================================
'''Build Topology'''
#======================================================================
#Define topology parameters
topo_recipe = {
'name':'cubic_1',
'domain_size': [],  #physical network size [meters]
'divisions': [35,35,35], #Number of pores in each direction
'lattice_spacing': [0.0001],  #spacing between pores [meters]
}
#Add topology to network
topo = OpenPNM.Topology.Cubic().generate(network=pn, **topo_recipe)
pn.set_type_definitions({'internal':0,'external':1,'inlet':2,'outlet':3})


b = (pn.pore_properties['coords'][:,0] <= 5e-5)*2
pn.set_pore_data('type',b)

#======================================================================
'''Build Geometry'''
#======================================================================
geom_recipe = {
'name': 'stick_and_ball',
'pore_seed': {'method': 'random'},
'throat_seed': {'method': 'neighbor_min'},
'pore_diameter': {'method': 'sphere',
                 'name': 'weibull_min',
                 'shape': 2.5,
                 'loc': 6e-6,
                 'scale': 2e-5},
'throat_diameter': {'method': 'cylinder',
                   'name': 'weibull_min',
                   'shape': 2.5,
                   'loc': 6e-6,
                   'scale': 2e-5},
'pore_volume': {'method': 'sphere'},
'throat_volume': {'method': 'cylinder'},
'throat_length': {'method': 'straight'},
}
geom = OpenPNM.Geometry.GenericGeometry().create(network=pn,**geom_recipe)

#======================================================================
'''Build Fluids'''
#======================================================================
#Define the fluids properties
air_recipe = {
'name': 'air',
'Pc': 3.771e6,
'Tc': 132.65,
'MW': 0.0291,
'diffusivity': {'method': 'Fuller',
                'MA': 0.03199,
                'MB': 0.0291,
                'vA': 16.3,
                'vB': 19.7},
'viscosity': {'method': 'Reynolds',
              'uo': 0.001,
              'b': 0.1},
'molar_density': {'method': 'ideal_gas',
                  'R': 8.314},
}
air = OpenPNM.Fluids.GenericFluid(loggername='AIR',loglevel=20).create(network=pn,**air_recipe)

water_recipe = {
'name': 'water',
'Pc': 2.206e6,
'Tc': 647,
'MW': 0.0181,
'diffusivity': {'method': 'constant',
                'value': 1e-12},
'viscosity': {'method': 'constant',
              'value': 0.001},
'molar_density': {'method': 'constant',
                  'value': 44445},
'surface_tension': {'method': 'constant',
                    'value': 0.072},
'contact_angle': {'method': 'constant',
                  'value': 110},
}
water = OpenPNM.Fluids.GenericFluid(loggername='WATER',loglevel=20).create(network=pn,**water_recipe)

#======================================================================
'''Build Physics Objects'''
#======================================================================
phys_recipe = {
'name': 'standard_water_physics',
'capillary_pressure': { 'method': 'purcell',
                        'r_toroid':1e-5},
'hydraulic_conductance': {'method': 'hagen_poiseuille'},
'diffusive_conductance': {'method': 'bulk_diffusion'},
}
phys_water = OpenPNM.Physics.GenericPhysics().create(network=pn,fluid=water,**phys_recipe)

phys_recipe = {
'name': 'standard_air_physics',
'hydraulic_conductance': {'method': 'hagen_poiseuille'},
'diffusive_conductance': {'method': 'bulk_diffusion'},
}
phys_air = OpenPNM.Physics.GenericPhysics().create(network=pn,fluid=air,**phys_recipe)

#======================================================================
'''Begin Simulations'''
#======================================================================
'''Perform a Drainage Experiment (OrdinaryPercolation)'''
#----------------------------------------------------------------------
#Initialize algorithm object
OP_1 = OpenPNM.Algorithms.OrdinaryPercolation(loglevel=10)
a = pn.get_pore_data('type') == pn.get_type_definitions(['inlet']).number
#Run algorithm
OP_1.run(network=pn,invading_fluid='water',defending_fluid='air',inlets=a,npts=10,AL=True)
OP_1.plot_drainage_curve()

#b = pn.pore_properties['coords'][:,1] <= 5e-5
#OP_1.evaluate_trapping(outlets=b)


##----------------------------------------------------------------------
#'''Perform an Injection Experiment (InvasionPercolation)'''
##----------------------------------------------------------------------
##Initialize algorithm object
#IP_1 = OpenPNM.Algorithms.InvasionPercolation()
##Apply desired/necessary pore scale physics methods
#OpenPNM.Physics.CapillaryPressure.Washburn(pn,water2)
#face = pn.pore_properties['type']==3
#quarter = sp.rand(pn.get_num_pores(),)<.1
#inlets = pn.pore_properties['numbering'][face&quarter]
#outlets = pn.pore_properties['numbering'][pn.pore_properties['type']==4]
#IP_1.run(pn,invading_fluid=water2,defending_fluid=air2,inlets=inlets,outlets=outlets)
#
##----------------------------------------------------------------------
#'''Performm a Diffusion Simulation on Partially Filled Network'''
##----------------------------------------------------------------------
##Apply desired/necessary pore scale physics methods
#air.regenerate()
#water.regenerate()
#OpenPNM.Physics.MultiPhase.update_occupancy_OP(water,Pc=8000)
#OpenPNM.Physics.MultiPhase.effective_occupancy(pn,air)
#OpenPNM.Physics.MassTransport.DiffusiveConductance(pn,air)
##Initialize algorithm object
#Fickian_alg = OpenPNM.Algorithms.FickianDiffusion()
##Create boundary condition arrays
#BCtypes = sp.zeros(pn.get_num_pores())
#BCvalues = sp.zeros(pn.get_num_pores())
##Specify Dirichlet-type and assign values
#BCtypes[pn.pore_properties['type']==2] = 1
#BCtypes[pn.pore_properties['type']==5] = 1
#BCvalues[pn.pore_properties['type']==2] = 8e-2
#BCvalues[pn.pore_properties['type']==5] = 8e-1
##Neumann
##BCtypes[pn.pore_properties['type']==1] = 1
##BCtypes[pn.pore_properties['type']==6] = 4
##BCvalues[pn.pore_properties['type']==1] = 8e-1
##BCvalues[pn.pore_properties['type']==6] = 2e-10
#Fickian_alg.set_boundary_conditions(types=BCtypes,values=BCvalues)
##Run simulation
#Fickian_alg.run(pn,active_fluid=air)
#
#
##Export to VTK
#OpenPNM.Visualization.VTK().write(pn,fluid=water)
