// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::c5c19023-7070-46f7-97e3-09f955c9c21a][c5c19023-7070-46f7-97e3-09f955c9c21a]]
use std::error::Error;
use std::io::{self, BufReader};
use std::io::prelude::*;
use std::fs::File;

pub mod linear;
pub mod octree;
// c5c19023-7070-46f7-97e3-09f955c9c21a ends here

// [[file:~/Workspace/Programming/chem-utils/chem-utils.note::34ebf4ed-5677-4f45-bb0c-4d8fb22bc514][34ebf4ed-5677-4f45-bb0c-4d8fb22bc514]]
pub fn get_positions_from_xyz_stream(txt: &str) -> Result<Vec<[f64; 3]>, Box<Error>> {
    let mut positions = Vec::new();

    for line in txt.lines() {
        let attrs: Vec<_> = line.split_whitespace().collect();
        let (symbol, position) = attrs.split_first().ok_or("encountering empty line")?;
        if position.len() != 3 {
            let msg = format!("informal xyz records: {}", line);
            Err(msg)?;
        }

        let p: Vec<f64> = position.iter().map(|x| x.parse().unwrap()).collect();
        positions.push([p[0], p[1], p[2]]);
    }

    Ok(positions)
}

// in a simple and dirty way
pub fn get_positions_from_xyzfile(filename: &str) -> Result<Vec<[f64; 3]>, Box<Error>> {
    let mut buffer = String::new();
    let f = File::open(filename)?;
    let mut f = BufReader::new(f);

    f.read_line(&mut buffer);
    f.read_line(&mut buffer);
    buffer.clear();

    f.read_to_string(&mut buffer)?;
    get_positions_from_xyz_stream(&buffer)
}
// 34ebf4ed-5677-4f45-bb0c-4d8fb22bc514 ends here
