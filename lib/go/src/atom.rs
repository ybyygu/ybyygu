// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::97aedb7c-dd99-4150-a90a-57f2e536dc78][97aedb7c-dd99-4150-a90a-57f2e536dc78]]
pub enum Element {
    H,
    He,
    Li,
}

pub struct Atom {
    pub index: usize,
    pub symbol: Element,
    pub name: String,
    pub position: [f64; 3],
    pub charge: f64,
}
// 97aedb7c-dd99-4150-a90a-57f2e536dc78 ends here
