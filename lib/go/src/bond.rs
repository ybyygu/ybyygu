// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::6d7f16c6-a551-425d-8cbe-e02585ef91f5][6d7f16c6-a551-425d-8cbe-e02585ef91f5]]
use std::fmt;
use std::u64;

#[derive(Clone, Debug)]
pub enum BondType {
    NotConnected,
    Partial,
    Single,
    Aromatic,
    Double,
    Triple,
    Quadruple,
}

#[derive(Clone, Debug)]
pub struct Bond {
    order: f64,
    kind : BondType,
    length: f64,                // for caching
    name: String,
}

impl Bond {
    pub fn new() -> Self{
        Bond {
            order: 1.0,
            kind: BondType::Single,
            length: 0.0,
            name: String::new(),
        }
    }
}

#[test]
fn test_bond() {
    let mut b = Bond::new();
    b.order = 1.2;
    b.name = "c1-c2".to_string();
    b.length = 2.5;
    println!("{:?}", b);
}
// 6d7f16c6-a551-425d-8cbe-e02585ef91f5 ends here
