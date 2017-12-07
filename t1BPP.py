# -*- coding: utf-8 -*-
"""
This module provides
- molarity()
calculate the molarity of a solution given the substance or molar Mass of the solute and the volume

- t1()
calculate the T1 for a given nucleus based on the BPP formula referenced therein.
"""
import sys

import numpy as np
import scipy.constants as const

from scipy.constants import N_A

import gammaList as gL

molarMasses = {"GdCl3" : 263.61, "TEMPO" : 156.25, "Trityl" : 1426.8, "TEMPOL" : 172.25}
spins = {"GdCl3" : 7./2, "TEMPO" : 1./2, "Trityl": 1./2, "TEMPOL" : 1./2}

eta = {"water" : 1.002e-3, "water-glycerol" : 8e-3}

def molarity(mass, radical, volume, molarMass = 0):
    """calculate molar concentration, i.e. moles for 1 L
    mass: mass of the molecule in gramm
    volume: solvent volume in L
    """
    if len(molecule) > 0:
        assert radical in list(molarMasses.keys()), "unknown molecule"
        molarMass = molarMasses[radical]
    else:
        assert molarMass > 0, "Molar Mass not specified."

    concentration = mass / molarMass / volume

    return concentration

def t1(concentration, radical, solvent, nucleus, T = 300):
    """Use BPP formula to calculate T1 in CGS units.
    The formula is Eq. 54 in
    Bloembergen, Purcell, Pound
    Relaxation Effects in Nuclear Magnetic Resonance Absorption
    Physical Review 73, 8, 1948

    concentration: molarity of the radical as calculated by molarity()
    radical: name of radical, e.g. Trityl, TEMPO or TEMPOL
    solvent: solvent (endoces viscosity information).
    nucleus: Nucleus for which T1 is calculated, e.g. 1H or 13C
    T: temperature (Kelvin)
    """
    S = spins[radical]
    J = S
    L = 0
    
    g0 = 2.0023193043622;#electron g factor, Wikipedia.
    gJLS = 1./2*(g0 + 1) - 1./2*(g0-1)*(L*(L+1) - S*(S+1))/(J*(J+1))

    muBohrCGS = 9.274*1e-21
    p = gJLS*np.sqrt(J*(J+1))
    muEffCGS = p*muBohrCGS

    etaCGS = eta[solvent]

    # boltzmann constant in cgs units
    kCGS = 1.3807e-16

    gammaCGS = gL.get(nucleus) / 1e4

    NIon = concentration * N_A / 1000

    t1Inv = 12*np.pi**2*gammaCGS**2*etaCGS*NIon*muEffCGS**2/(5*kCGS*T)

    T1 = 1/t1Inv

    print(("T1 is {0} ms".format(T1*1e3)))
    return T1


if __name__ == "__main__":
    molecule = "GdCl3"
    mass = 52e-3
    volume = 1e-3

    molarConcentration = molarity(mass, molecule, volume)
    print("We have a {} molar solution of {}".format(molarConcentration, molecule))

    t1This = t1(molarConcentration, molecule, "water", "1H")
    print("T1 calculated: {} ms".format(t1This*1000))

    #TEMPO in water and carbon
    molecule = "TEMPOL"
    mass = 300e-3
    volume = 1e-3

    molarConcentration = molarity(mass, molecule, volume)
    print("We have a {} molar solution of {}".format(molarConcentration, molecule))

    t1This = t1(molarConcentration, molecule, "water-glycerol", "13C")
    print("T1 calculated: {} ms".format(t1This*1000))


    print(" Trityl and Pyruvic Acid")
    print("========================")
    molcarConcentration = 50e-3
    t1This = t1(molarConcentration, "Trityl", "water", "13C")
    print("T1 calculated: {} ms".format(t1This*1000))

    print("Trityl and Naphthalene")
    print("======================")
    molarConcentration = 20e-3
    t1This = t1(molarConcentration, "Trityl", "water", "13C")
    print("T1 calculated: {} s".format(t1This))
    


