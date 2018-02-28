// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::97aedb7c-dd99-4150-a90a-57f2e536dc78][97aedb7c-dd99-4150-a90a-57f2e536dc78]]
use std::fmt::{self, Debug, Display};

static ElementArray: [&'static str; 118] = [
    "X",
    "H",
    "He",
    "Li",
    "Be",
    "B",
    "N",
    "O",
    "F",
    "Ne",
    "Na",
    "Mg",
    "Al",
    "Si",
    "P",
    "S",
    "Cl",
    "Ar",
    "K",
    "Ca",
    "Sc",
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Cu",
    "Zn",
    "Ga",
    "Ge",
    "As",
    "Se",
    "Br",
    "Kr",
    "Rb",
    "Sr",
    "Y",
    "Zr",
    "Nb",
    "Mo",
    "Tc",
    "Ru",
    "Rh",
    "Pd",
    "Ag",
    "Cd",
    "In",
    "Sn",
    "Sb",
    "Te",
    "I",
    "Xe",
    "Cs",
    "Ba",
    "La",
    "Ce",
    "Pr",
    "Nd",
    "Pm",
    "Sm",
    "Eu",
    "Gd",
    "Tb",
    "Dy",
    "Ho",
    "Er",
    "Tm",
    "Yb",
    "Lu",
    "Hf",
    "Ta",
    "W",
    "Re",
    "Os",
    "Ir",
    "Pt",
    "Au",
    "Hg",
    "Tl",
    "Pb",
    "Bi",
    "Po",
    "At",
    "Rn",
    "Fr",
    "Ra",
    "Ac",
    "Th",
    "Pa",
    "U",
    "Np",
    "Pu",
    "Am",
    "Cm",
    "Bk",
    "Cf",
    "Es",
    "Fm",
    "Mv",
    "No",
    "Lr",
    "Rf",
    "Db",
    "Sg",
    "Bh",
    "Hs",
    "Mt",
    "Uun",
    "Uuu",
    "Uub",
    "Uut",
    "Uuq",
    "Uup",
    "Uuh",
    "Uus",
    "Uuo",
];

#[derive(Debug, Copy, Clone)]
pub enum Element {
    X,
    H,
    He,
    Li,
    Be,
    B,
    N,
    O,
    F,
    Ne,
    Na,
    Mg,
    Al,
    Si,
    P,
    S,
    Cl,
    Ar,
    K,
    Ca,
    Sc,
    Ti,
    V,
    Cr,
    Mn,
    Fe,
    Co,
    Ni,
    Cu,
    Zn,
    Ga,
    Ge,
    As,
    Se,
    Br,
    Kr,
    Rb,
    Sr,
    Y,
    Zr,
    Nb,
    Mo,
    Tc,
    Ru,
    Rh,
    Pd,
    Ag,
    Cd,
    In,
    Sn,
    Sb,
    Te,
    I,
    Xe,
    Cs,
    Ba,
    La,
    Ce,
    Pr,
    Nd,
    Pm,
    Sm,
    Eu,
    Gd,
    Tb,
    Dy,
    Ho,
    Er,
    Tm,
    Yb,
    Lu,
    Hf,
    Ta,
    W,
    Re,
    Os,
    Ir,
    Pt,
    Au,
    Hg,
    Tl,
    Pb,
    Bi,
    Po,
    At,
    Rn,
    Fr,
    Ra,
    Ac,
    Th,
    Pa,
    U,
    Np,
    Pu,
    Am,
    Cm,
    Bk,
    Cf,
    Es,
    Fm,
    Mv,
    No,
    Lr,
    Rf,
    Db,
    Sg,
    Bh,
    Hs,
    Mt,
    Uun,
    Uuu,
    Uub,
    Uut,
    Uuq,
    Uup,
    Uuh,
    Uus,
    Uuo,
// beryllium     =  ("Be", 4)
// boron         =  ("B",  5)
// carbon        =  ("C",  6)
// nitrogen      =  ("N",  7)
// oxygen        =  ("O",  8)
// fluorine      =  ("F",  9)
// neon          =  ("Ne", 10)
// sodium        =  ("Na", 11)
// magnesium     =  ("Mg", 12)
// aluminum      =  ("Al", 13)
// silicon       =  ("Si", 14)
// phosphorus    =  ("P",  15)
// sulfur        =  ("S",  16)
// chlorine      =  ("Cl", 17)
// argon         =  ("Ar", 18)
// potassium     =  ("K",  19)
// calcium       =  ("Ca", 20)
// scandium      =  ("Sc", 21)
// titanium      =  ("Ti", 22)
// vanadium      =  ("V",  23)
// chromium      =  ("Cr", 24)
// manganese     =  ("Mn", 25)
// iron          =  ("Fe", 26)
// cobalt        =  ("Co", 27)
// nickel        =  ("Ni", 28)
// copper        =  ("Cu", 29)
// zinc          =  ("Zn", 30)
// gallium       =  ("Ga", 31)
// germanium     =  ("Ge", 32)
// arsenic       =  ("As", 33)
// selenium      =  ("Se", 34)
// bromine       =  ("Br", 35)
// krypton       =  ("Kr", 36)
// rubidium      =  ("Rb", 37)
// strontium     =  ("Sr", 38)
// yttrium       =  ("Y" , 39)
// zirconium     =  ("Zr", 40)
// niobium       =  ("Nb", 41)
// molybdenum    =  ("Mo", 42)
// technetium    =  ("Tc", 43)
// ruthenium     =  ("Ru", 44)
// rhodium       =  ("Rh", 45)
// palladium     =  ("Pd", 46)
// silver        =  ("Ag", 47)
// cadmium       =  ("Cd", 48)
// indium        =  ("In", 49)
// tin           =  ("Sn", 50)
// antimony      =  ("Sb", 51)
// tellurium     =  ("Te", 52)
// iodine        =  ("I",  53)
// xenon         =  ("Xe", 54)
// cesium        =  ("Cs", 55)
// barium        =  ("Ba", 56)
// lanthanum     =  ("La", 57)
// cerium        =  ("Ce", 58)
// praesodymium  =  ("Pr", 59)
// neodymium     =  ("Nd", 60)
// promethium    =  ("Pm", 61)
// samarium      =  ("Sm", 62)
// europium      =  ("Eu", 63)
// gadolinium    =  ("Gd", 64)
// terbium       =  ("Tb", 65)
// dyprosium     =  ("Dy", 66)
// holmium       =  ("Ho", 67)
// erbium        =  ("Er", 68)
// thulium       =  ("Tm", 69)
// ytterbium     =  ("Yb", 70)
// lutetium      =  ("Lu", 71)
// hafnium       =  ("Hf", 72)
// tantalium     =  ("Ta", 73)
// wolfram       =  ("W",  74)
// rhenium       =  ("Re", 75)
// osmium        =  ("Os", 76)
// iridium       =  ("Ir", 77)
// platinum      =  ("Pt", 78)
// gold          =  ("Au", 79)
// mercury       =  ("Hg", 80)
// thallium      =  ("Tl", 81)
// lead          =  ("Pb", 82)
// bismuth       =  ("Bi", 83)
// polonium      =  ("Po", 84)
// astatine      =  ("At", 85)
// radon         =  ("Rn", 86)
// francium      =  ("Fr", 87)
// radium        =  ("Ra", 88)
// actinium      =  ("Ac", 89)
// thorium       =  ("Th", 90)
// protactinium  =  ("Pa", 91)
// uranium       =  ("U",  92)
// neptunium     =  ("Np", 93)
// plutonium     =  ("Pu", 94)
// americium     =  ("Am", 95)
// curium        =  ("Cm", 96)
// berkelium     =  ("Bk", 97)
// californium   =  ("Cf", 98)
// einsteinium   =  ("Es", 99)
// fermium       =  ("Fm", 100)
// mendelevium   =  ("Mv", 101)
// nobelium      =  ("No", 102)
// lawrencium    =  ("Lr", 103)
// rutherfordium =  ("Rf", 104)
// dubnium       =  ("Db", 105)
// seaborgium    =  ("Sg", 106)
// bohrium       =  ("Bh", 107)
// hassium       =  ("Hs", 108)
// meitnerium    =  ("Mt", 109)
// ununnilium    =  ("Uun", 110)
// unununium     =  ("Uuu", 111)
// ununbium      =  ("Uub", 112)
// ununtrium     =  ("Uut", 113)
// ununquadium   =  ("Uuq", 114)
// ununpentium   =  ("Uup", 115)
// ununhexium    =  ("Uuh", 116)
// ununseptium   =  ("Uus", 117)
// ununoctium    =  ("Uuo", 118)
}

impl fmt::Display for Element {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{:?}", self)
    }
}

// impl FromStr for Element {
//     type Err = ();
//     fn from_str(s: &str) -> Result<Self, Self::Err> {
//         match s {

//         }
// }

impl Element {
    fn symbol(&self) -> String {
        format!("{:?}", self)
    }

    fn number(&self) -> usize {
        *self as usize
    }
}

pub struct Atom {
    pub index: usize,
    pub symbol: String,
    pub name: String,
    pub position: [f64; 3],
    pub charge: f64,
}


#[test]
fn test_element() {
    let x = Element::X;
    println!("{:}", x);
    println!("symbol = {:}", x.symbol());
    println!("number = {:}", x.number());

    let x = Element::H;
    println!("{:}", x);
    println!("symbol = {:}", x.symbol());
    println!("number = {:}", x.number());
}
// 97aedb7c-dd99-4150-a90a-57f2e536dc78 ends here
