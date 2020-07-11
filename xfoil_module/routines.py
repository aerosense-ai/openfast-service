import numpy as np
from xfoil import XFoil

import os
import sys
import contextlib


xf = XFoil()  # create xfoil object


def call(twine_config, twine_input_values):
    '''Calls Xfoil module'''
    print("Lets run Xfoil!")
    # Hardcoded airfoil names for now
    # TODO add multi-processing, each section on a separate sub-process.
    airfoil_name = 'naca_0012'
    xf.airfoil = load_airfoil(airfoil_name)

    xf.Re = set_input(twine_input_values)[0] #set reynolds number in xfoil
    xf.Re = 6e6
    # Force transition location based on Critical Reynolds
    # TODO implement as an input switch, to force the transition based on research for
    #      Critical Reynolds Number dependency from leading edge erosion
    #      Default xtr is (1,1)
    # xf.xtr = set_input(twine_input_values)[1]  # Set xtr value (xtr top, xtr bot), should be a tuple
    # n_crit Default value is 9 which corresponds to 7% TI level.
    xf.n_crit = 9
    xf.max_iter = 100  # Hardcoded for now

    # Setting Mach number before assigning airfoil throws in the error.
    # BUG in xfoil-python 1.1.1 !! Changing Mach number has no effect on results!
    # There seems to be confusion between MINf and MINf1, adding a line MINf1 = M
    # after line 204 of the api.f90, seems to solve the issue.
    xf.M = twine_input_values['mach_number']
    # Feed the AoA range to Xfoil and perfom the analysis
    # The result contains following vectors AoA, Cl, Cd, Cm, Cp
    with stdchannel_redirected(sys.stdout, os.devnull):  # redirects output to devnull
        result = xf.aseq(twine_config['alpha_range'][0],
                         twine_config['alpha_range'][1],
                         twine_config['alpha_range'][2])

    # TODO results probably should be a dictionary
    results = [airfoil_name, result]

    return results


def set_input(_in):
    # Calculate Reynolds from input values
    reynolds = _in['inflow_speed'] * _in['characteristic_length'] / _in['kinematic_viscosity']
    # Calculate x-transition from Critical Reynolds
    x_transition = tuple(_xtr / reynolds for _xtr in _in['re_xtr'])
    return reynolds, x_transition


def load_airfoil(airfoil_name):
    with open('./data/input/datasets/aerofoil_shape_file/' + airfoil_name + '.dat') as f:
        content = f.readlines()

    x_coord = []
    y_coord = []

    for line in content[1:]:
        x_coord.append(float(line.split()[0]))
        y_coord.append(float(line.split()[1]))

    airfoilObj = xf.airfoil
    airfoilObj.x = np.array(x_coord)
    airfoilObj.y = np.array(y_coord)

    return airfoilObj

@contextlib.contextmanager
def stdchannel_redirected(std_channel, dest_filename):
    """
    A context manager to temporarily redirect stdout or stderr
    e.g.:
    with stdchannel_redirected(sys.stderr, os.devnull):
        if compiler.has_function('clock_gettime', libraries=['rt']):
            libraries.append('rt')
    """
    try:
        old_std_channel = os.dup(std_channel.fileno())
        dest_file = open(dest_filename, 'w')
        os.dup2(dest_file.fileno(), std_channel.fileno())
        yield
    finally:
        if old_std_channel is not None: os.dup2(old_std_channel, std_channel.fileno())
        if dest_file is not None: dest_file.close()

