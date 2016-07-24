def get(nucleus="", allNuclei = 0):
    """
    This function returns the gamma of any isotope based on the 2001 IUPAC
    Recommendations published in Pure Appl. Chem., Vol. 73, No. 11, pp.

    Usage: gammaList("63Cu")
    """

    #print "This is gammList"
    gammaListAll = {}

    gammaListAll["E"] = 1.7608597e11  

    #Spin 1/2 Isotopes
    gammaListAll["1H"] = 26.7522128e7#H
    gammaListAll["3He"] = -20.3801587e7#Helium, not Tritium
    gammaListAll["13C"] = 6.728284e7#Carbon
    gammaListAll["15N"] = -2.71261804e7#Nitrogen
    gammaListAll["19F"] = 25.18148e7#Fluor
    gammaListAll["29Si"] = -5.3190e7#Si
    gammaListAll["31P"] = 10.8394e7#Phosphor
    gammaListAll["57Fe"] = 0.8680624e7#Iron
    gammaListAll["77Se"] = 5.1253857e7#Selenium
    gammaListAll["89Y"] = -1.3162791e7#Yttrium
    gammaListAll["103Rh"] = -0.8468e7#Rhodium
    gammaListAll["107Ag"] = -1.0889181e7#Silver
    gammaListAll["109Ag"] = -1.2518634e7#Silver
    gammaListAll["111Cd"] = -5.6983131e7#Cadmium, not preferred
    gammaListAll["113Cd"] = -5.9609155e7#Cadmium, long-lived radioactive isotope
    gammaListAll["115Sn"] = -8.8013e7#Tin
    gammaListAll["117Sn"] = -9.58879e7#Tin
    gammaListAll["119Sn"] = -10.0317e7#Tin
    gammaListAll["123Te"] = -7.059098e7#Tellurium
    gammaListAll["125Te"] = -8.5108404e7#Tellur
    gammaListAll["129Xe"] = -7.452103e7#Xenon
    gammaListAll["183W"] = 1.1282403e7#Tungsten
    gammaListAll["187Os"] = 0.6192895e7#Osmium
    gammaListAll["195Pt"] = 5.8385e7#Platinum
    gammaListAll["199Hg"] = 4.8457913e7#Mercury
    gammaListAll["203Tl"] = 15.5393338e7#Thallium
    gammaListAll["205Tl"] = 15.6921808e7#Thallium
    gammaListAll["207Pb"] = 5.58046e7#Lead

    #Quadrupolar Isotopes
    gammaListAll["2H"] = 4.10662791e7#Deuterium, useful 1/2 isotope exists
    gammaListAll["6Li"] = 3.9371709e7#Lithium
    gammaListAll["7Li"] = 10.3977013e7#Lithium
    gammaListAll["9Be"] = -3.759666e7#Beryllium
    gammaListAll["10B"] = 2.8746786e7#Boron
    gammaListAll["11B"] = 8.5847044e7#Boron
    gammaListAll["14N"] = 1.9337792e7#Nitrogen, radioactive, with a long half-life
    gammaListAll["17O"] = -3.62808e7#Oxygen
    gammaListAll["21Ne"] = -2.11308e7#Neon
    gammaListAll["23Na"] = 7.0808493e7#Sodium
    gammaListAll["25Mg"] = -1.63887e7#Magnesium
    gammaListAll["27Al"] = 6.9762715e7#Aluminum
    gammaListAll["33As"] = 2.055685e7#Sulphur
    gammaListAll["35Cl"] = 2.624198e7#Chlorine
    gammaListAll["37Cl"] = 2.184368e7#Chlorine
    gammaListAll["39K"] = 1.2500608e7#Potassium
    gammaListAll["40K"] = -1.5542854e7#Potassium
    gammaListAll["41K"] = 0.68606808e7#Potassium
    gammaListAll["43Ca"] = -1.803069e7#Calcium
    gammaListAll["45Sc"] = 6.5087973e7#Scandium
    gammaListAll["47Ti"] = -1.5105e7#Titanium
    gammaListAll["49Ti"] = -1.51095e7#Titanium
    gammaListAll["50V"] = 2.6706490e7#Vanadium
    gammaListAll["51V"] = 7.0455117e7#Vanadium
    gammaListAll["53Cr"] = -1.5152e7#Chromium
    gammaListAll["55Mn"] = 6.6452546e7#Manganese
    gammaListAll["59Co"] = 6.332e7#Cobalt
    gammaListAll["61Ni"] = -2.3948e7#Nickel
    gammaListAll["63Cu"] = 7.1117890e7#Copper
    gammaListAll["65Cu"] = 7.60435e7#Copper
    gammaListAll["67Zn"] = 1.676688e7#Zinc
    gammaListAll["69Ga"] = 6.438855e7#Gallium
    gammaListAll["71Ga"] = 8.181171e7#Gallium
    gammaListAll["73Ge"] = -0.9360303e7#Germanium
    gammaListAll["75As"] = 4.596163e7#Arsenic
    gammaListAll["79Br"] = 6.725616e7#Bromine, not preferred
    gammaListAll["81Br"] =7.249776e7#Bromine
    gammaListAll["83Kr"] = -1.03310e7#Krypton
    gammaListAll["85Rb"] = 2.5927050e7#Rubidium
    gammaListAll["87Rb"] = 8.786400e7#Rubidium, radioactive, with a long half-life
    gammaListAll["87Sr"] = -1.1639376e7#Strontium
    gammaListAll["91Zr"] = -2.49743e7#Zirconium
    gammaListAll["93Nb"] =  6.5674e7#Niobium
    gammaListAll["95Mo"] = -1.751e7#Molybdenum
    gammaListAll["97Mo"] = -1.788e7#Molybdenum
    gammaListAll["99Tc"] = 6.046e7#Technetium, radioactive, with a long half-life
    gammaListAll["99Ru"] = -1.229e7#%Ruthenium
    gammaListAll["101Ru"] = -1.377e7#Ruthenium
    gammaListAll["105Pd"] = -1.23e7#Palladium
    gammaListAll["113In"] = 5.8845e7#Indium
    gammaListAll["115In"] = 5.8972e7#Indium
    gammaListAll["121Sb"] = 6.4435e7#Antimony
    gammaListAll["123Sb"] = 3.4892e7#Antimony
    gammaListAll["127I"] = 5.389573e7#Iodine
    gammaListAll["131Xe"] = 2.209076e7#Xenon
    gammaListAll["133Cs"] = 3.5332539e7#Caesium
    gammaListAll["135Ba"] = 2.67550e7#Barium
    gammaListAll["137Ba"] = 2.99295e7#Barium
    gammaListAll["138La"] = 3.557239e7#Lanthanum, radioacitve, long half-life
    gammaListAll["139La"] = 3.8083318e7#Lanthanum
    gammaListAll["177Hf"] = 1.086e7#Hafnium
    gammaListAll["179Hf"] = -0.6821e7#Hafnium
    gammaListAll["181Ta"] = 3.2438e7#Tantalum
    gammaListAll["185Re"] = 6.1057e7#Rhenium, not preferred
    gammaListAll["187Re"] = 6.1682e7#Rhenium, radioactive, long half-life
    gammaListAll["189Os"] = 2.10713e7#Osmium, a useful 1/2 isotope exists
    gammaListAll["191Ir"] = 0.4812e7#Iridium, not preferred
    gammaListAll["193Ir"] = 0.5227e7#Iridium
    gammaListAll["197Au"] = 0.473060e7#Gold
    gammaListAll["201Hg"] = -1.788769e7#Mercury, a useful 1/2 isotope exists
    gammaListAll["209Bi"] = 4.3750e7#Bismuth
 
    #Lanthanoids
    gammaListAll["141Pr"] = 8.1907e7#Praseodymium
    gammaListAll["143Nd"] =-1.457e7#Neodymium
    gammaListAll["145Nd"] =-0.898e7#Neodymium
    gammaListAll["147Sm"] =-1.115e7#Samarium, radioactive, with a long half-life
    gammaListAll["149Sm"] = -0.9192e7#Samarium
    gammaListAll["151Eu"] = 6.6510e7#Europium
    gammaListAll["153Eu"] = 2.9369e7#Europium
    gammaListAll["155Gd"] = -0.82132e7#Gadolinium
    gammaListAll["157Gd"] = -1.0769e7#Gadolinium
    gammaListAll["159Tb"] = 6.431e7#Terbium
    gammaListAll["161Dy"] = -0.9201e7#Dysprosium
    gammaListAll["163Dy"] = 1.289e7#Dysprosium
    gammaListAll["165Ho"] = 53.710e7#Holmium
    gammaListAll["167Er"] = -0.77157e7#Erbium
    gammaListAll["169Tm"] = -2.218e7#Thulium
    gammaListAll["171Yb"] = 4.7288e7#Ytterbium
    gammaListAll["173Yb"] = -1.3025e7#Ytterbium


    gammaListAll["175Lu"] =3.0552e7#Lutetium, seems not to be a Lanthanoid, group 3
    gammaListAll["176Lu"] = 2.1684e7#Lutetium, radioactive, with a long half-life
    gammaListAll["235U"] = -0.52e7#Uranium


    if allNuclei == 1:
        print "We return all Nuclei"
        gamma = gammaListAll
    else:
        gamma = gammaListAll[nucleus];

    return gamma

def gammaList(nucleus):
    """Returns the same as get(),
    included for backward-compatiblity."""
    return get(nucleus)

if __name__ == "__main__":
    print gamma.__doc__
