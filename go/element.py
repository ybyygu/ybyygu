#! /usr/bin/env python3
# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::f1974825-5d2d-42d2-8af8-cdecc4134c89][f1974825-5d2d-42d2-8af8-cdecc4134c89]]
#===============================================================================#
#   DESCRIPTION:  GO: a Graph-based chemical Objects library
#
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#         NOTES:  ---
#        AUTHOR:  Wenping Guo <ybyygu@gmail.com>
#       LICENCE:  GPL version 2 or upper
#       CREATED:  <2006-08-30 Wed 16:51>
#       UPDATED:  <2017-11-03 Fri 16:24>
#===============================================================================#

from enum import Enum

from . import attr

class Element(Enum):
    """
    Basic immutable element object with relevant properties.

    Args:
        symbol (str): Element symbol, e.g., `H', `Fe'

    .. attribute:: symbol

        Element symbol

    .. attribute:: number

        Atomic number

    .. attribute:: name

       Long name for element. E.g., `hydrogen'.
    """

    dummy         =  ("X",  0)
    hydrogen      =  ("H" , 1)
    helium        =  ("He", 2)
    lithium       =  ("Li", 3)
    beryllium     =  ("Be", 4)
    boron         =  ("B",  5)
    carbon        =  ("C",  6)
    nitrogen      =  ("N",  7)
    oxygen        =  ("O",  8)
    fluorine      =  ("F",  9)
    neon          =  ("Ne", 10)
    sodium        =  ("Na", 11)
    magnesium     =  ("Mg", 12)
    aluminum      =  ("Al", 13)
    silicon       =  ("Si", 14)
    phosphorus    =  ("P",  15)
    sulfur        =  ("S",  16)
    chlorine      =  ("Cl", 17)
    argon         =  ("Ar", 18)
    potassium     =  ("K",  19)
    calcium       =  ("Ca", 20)
    scandium      =  ("Sc", 21)
    titanium      =  ("Ti", 22)
    vanadium      =  ("V",  23)
    chromium      =  ("Cr", 24)
    manganese     =  ("Mn", 25)
    iron          =  ("Fe", 26)
    cobalt        =  ("Co", 27)
    nickel        =  ("Ni", 28)
    copper        =  ("Cu", 29)
    zinc          =  ("Zn", 30)
    gallium       =  ("Ga", 31)
    germanium     =  ("Ge", 32)
    arsenic       =  ("As", 33)
    selenium      =  ("Se", 34)
    bromine       =  ("Br", 35)
    krypton       =  ("Kr", 36)
    rubidium      =  ("Rb", 37)
    strontium     =  ("Sr", 38)
    yttrium       =  ("Y" , 39)
    zirconium     =  ("Zr", 40)
    niobium       =  ("Nb", 41)
    molybdenum    =  ("Mo", 42)
    technetium    =  ("Tc", 43)
    ruthenium     =  ("Ru", 44)
    rhodium       =  ("Rh", 45)
    palladium     =  ("Pd", 46)
    silver        =  ("Ag", 47)
    cadmium       =  ("Cd", 48)
    indium        =  ("In", 49)
    tin           =  ("Sn", 50)
    antimony      =  ("Sb", 51)
    tellurium     =  ("Te", 52)
    iodine        =  ("I",  53)
    xenon         =  ("Xe", 54)
    cesium        =  ("Cs", 55)
    barium        =  ("Ba", 56)
    lanthanum     =  ("La", 57)
    cerium        =  ("Ce", 58)
    praesodymium  =  ("Pr", 59)
    neodymium     =  ("Nd", 60)
    promethium    =  ("Pm", 61)
    samarium      =  ("Sm", 62)
    europium      =  ("Eu", 63)
    gadolinium    =  ("Gd", 64)
    terbium       =  ("Tb", 65)
    dyprosium     =  ("Dy", 66)
    holmium       =  ("Ho", 67)
    erbium        =  ("Er", 68)
    thulium       =  ("Tm", 69)
    ytterbium     =  ("Yb", 70)
    lutetium      =  ("Lu", 71)
    hafnium       =  ("Hf", 72)
    tantalium     =  ("Ta", 73)
    wolfram       =  ("W",  74)
    rhenium       =  ("Re", 75)
    osmium        =  ("Os", 76)
    iridium       =  ("Ir", 77)
    platinum      =  ("Pt", 78)
    gold          =  ("Au", 79)
    mercury       =  ("Hg", 80)
    thallium      =  ("Tl", 81)
    lead          =  ("Pb", 82)
    bismuth       =  ("Bi", 83)
    polonium      =  ("Po", 84)
    astatine      =  ("At", 85)
    radon         =  ("Rn", 86)
    francium      =  ("Fr", 87)
    radium        =  ("Ra", 88)
    actinium      =  ("Ac", 89)
    thorium       =  ("Th", 90)
    protactinium  =  ("Pa", 91)
    uranium       =  ("U",  92)
    neptunium     =  ("Np", 93)
    plutonium     =  ("Pu", 94)
    americium     =  ("Am", 95)
    curium        =  ("Cm", 96)
    berkelium     =  ("Bk", 97)
    californium   =  ("Cf", 98)
    einsteinium   =  ("Es", 99)
    fermium       =  ("Fm", 100)
    mendelevium   =  ("Mv", 101)
    nobelium      =  ("No", 102)
    lawrencium    =  ("Lr", 103)
    rutherfordium =  ("Rf", 104)
    dubnium       =  ("Db", 105)
    seaborgium    =  ("Sg", 106)
    bohrium       =  ("Bh", 107)
    hassium       =  ("Hs", 108)
    meitnerium    =  ("Mt", 109)
    ununnilium    =  ("Uun", 110)
    unununium     =  ("Uuu", 111)
    ununbium      =  ("Uub", 112)
    ununtrium     =  ("Uut", 113)
    ununquadium   =  ("Uuq", 114)
    ununpentium   =  ("Uup", 115)
    ununhexium    =  ("Uuh", 116)
    ununseptium   =  ("Uus", 117)
    ununoctium    =  ("Uuo", 118)

    def __new__(cls, symbol, number):
        obj = object.__new__(cls)
        obj._value_ = symbol
        cls._value2member_map_[number] = obj
        return obj

    def __init__(self, atomic_symbol, atomic_number):
        self.symbol = atomic_symbol
        self.number = atomic_number

    def __eq__(self, other):
        if isinstance(other, Element):
            return self.symbol == other.symbol

        if isinstance(other, str):
            return self.symbol == other

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.symbol)

    def __repr__(self):
        return "Element " + self.symbol

    def __str__(self):
        return self.symbol
# f1974825-5d2d-42d2-8af8-cdecc4134c89 ends here
